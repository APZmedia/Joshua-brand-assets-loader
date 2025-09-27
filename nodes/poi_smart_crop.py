# poi_smart_crop.py
import math
import numpy as np
from PIL import Image
import torch

try:
    import cv2  # optional
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False


def _to_uint8(img_tensor: torch.Tensor) -> np.ndarray:
    # img_tensor: [H, W, C], 0..1 float
    arr = (img_tensor.clamp(0, 1).cpu().numpy() * 255.0).astype(np.uint8)
    return arr


def _to_tensor(img_np: np.ndarray) -> torch.Tensor:
    # img_np: HWC uint8
    t = torch.from_numpy(img_np.astype(np.float32) / 255.0)
    return t


def spectral_residual_saliency(gray: np.ndarray) -> np.ndarray:
    """
    Enhanced saliency detection with better thresholding.
    Input gray uint8 [H,W], returns float32 saliency 0..1
    """
    # ensure float
    g = gray.astype(np.float32) / 255.0
    h, w = g.shape
    
    # FFT
    G = np.fft.fft2(g)
    A = np.abs(G)
    L = np.log(A + 1e-8)
    
    # average filter on log amplitude (using simple box blur)
    kernel = 3
    pad = kernel // 2
    L_pad = np.pad(L, ((pad, pad), (pad, pad)), mode="reflect")
    L_avg = (
        L_pad[:-2, :-2] + L_pad[:-2, 1:-1] + L_pad[:-2, 2:] +
        L_pad[1:-1, :-2] + L_pad[1:-1, 1:-1] + L_pad[1:-1, 2:] +
        L_pad[2:, :-2] + L_pad[2:, 1:-1] + L_pad[2:, 2:]
    ) / 9.0
    R = L - L_avg
    
    # reconstruct
    S = np.abs(np.fft.ifft2(np.exp(R) * np.exp(1j * np.angle(G))))
    
    # smooth with smaller sigma for more focused detection
    from scipy.ndimage import gaussian_filter
    S = gaussian_filter(S, sigma=1.0)
    
    # Apply thresholding to focus on high-saliency regions
    # Remove low-saliency areas more aggressively
    threshold = np.percentile(S, 70)  # Keep only top 30% of saliency values
    S = np.where(S > threshold, S, 0)
    
    # Normalize
    S -= S.min()
    if S.max() > 0:
        S /= S.max()
    
    # Apply additional smoothing to create more focused regions
    S = gaussian_filter(S, sigma=0.5)
    
    return S.astype(np.float32)


def _weighted_percentile_indices(weights_1d: np.ndarray, lower=0.05, upper=0.95):
    # weights_1d: length N, nonnegative
    w = weights_1d.astype(np.float64)
    total = w.sum()
    if total <= 0:
        return 0, len(w) - 1
    cdf = np.cumsum(w) / total
    lo_idx = int(np.clip(np.searchsorted(cdf, lower), 0, len(w) - 1))
    hi_idx = int(np.clip(np.searchsorted(cdf, upper), 0, len(w) - 1))
    return lo_idx, hi_idx


def _compute_median_box_from_saliency(S: np.ndarray, mass_clip=(0.05, 0.95)):
    """
    Dynamic automated box computation that adapts to image content.
    Returns (x0, y0, x1, y1) inclusive-exclusive in image coords.
    """
    h, w = S.shape
    
    # Check if saliency map has any meaningful content
    if S.sum() < 1e-6:
        # Return center region if no saliency
        center_x, center_y = w // 2, h // 2
        box_size = min(w, h) // 4
        return (center_x - box_size//2, center_y - box_size//2, 
                center_x + box_size//2, center_y + box_size//2)
    
    # Dynamic thresholding based on saliency distribution
    saliency_flat = S.flatten()
    saliency_flat = saliency_flat[saliency_flat > 0]  # Remove zeros
    
    if len(saliency_flat) == 0:
        # No meaningful saliency, return center
        center_x, center_y = w // 2, h // 2
        box_size = min(w, h) // 4
        return (center_x - box_size//2, center_y - box_size//2, 
                center_x + box_size//2, center_y + box_size//2)
    
    # Analyze saliency distribution to determine optimal threshold
    mean_saliency = np.mean(saliency_flat)
    std_saliency = np.std(saliency_flat)
    
    # Dynamic threshold: mean + 0.5 * std (adapts to content)
    dynamic_threshold = mean_saliency + 0.5 * std_saliency
    
    # Apply dynamic thresholding
    S_focused = np.where(S > dynamic_threshold, S, 0)
    
    # If thresholding removes too much, use a more conservative approach
    if S_focused.sum() < S.sum() * 0.05:  # Less than 5% remains
        # Use a more conservative threshold
        conservative_threshold = mean_saliency + 0.2 * std_saliency
        S_focused = np.where(S > conservative_threshold, S, 0)
        
        # If still too restrictive, use percentile-based approach
        if S_focused.sum() < S.sum() * 0.05:
            percentile_threshold = np.percentile(saliency_flat, 70)  # Top 30%
            S_focused = np.where(S > percentile_threshold, S, 0)
    
    # If still no meaningful content, use original with very light thresholding
    if S_focused.sum() < S.sum() * 0.01:
        S_focused = S
    
    # collapse to 1D distributions
    wy = S_focused.sum(axis=1)  # per-row weights
    wx = S_focused.sum(axis=0)  # per-col weights
    
    # Dynamic mass clipping based on content distribution
    # Analyze the weight distributions to determine optimal clipping
    wy_nonzero = wy[wy > 0]
    wx_nonzero = wx[wx > 0]
    
    if len(wy_nonzero) > 0 and len(wx_nonzero) > 0:
        # Calculate dynamic clipping based on weight distribution
        wy_mean, wy_std = np.mean(wy_nonzero), np.std(wy_nonzero)
        wx_mean, wx_std = np.mean(wx_nonzero), np.std(wx_nonzero)
        
        # Dynamic clipping: focus on regions with weights > mean - 0.5*std
        y_threshold = max(0, wy_mean - 0.5 * wy_std)
        x_threshold = max(0, wx_mean - 0.5 * wx_std)
        
        # Find indices where weights exceed threshold
        y_indices = np.where(wy > y_threshold)[0]
        x_indices = np.where(wx > x_threshold)[0]
        
        if len(y_indices) > 0 and len(x_indices) > 0:
            y0, y1 = y_indices[0], y_indices[-1] + 1
            x0, x1 = x_indices[0], x_indices[-1] + 1
        else:
            # Fallback to percentile-based approach
            y0, y1 = _weighted_percentile_indices(wy, 0.1, 0.9)
            x0, x1 = _weighted_percentile_indices(wx, 0.1, 0.9)
    else:
        # Fallback to original method
        y0, y1 = _weighted_percentile_indices(wy, 0.1, 0.9)
        x0, x1 = _weighted_percentile_indices(wx, 0.1, 0.9)

    # Ensure reasonable minimum size (at least 5% of image, max 50%)
    min_w, min_h = max(1, w // 20), max(1, h // 20)
    max_w, max_h = w // 2, h // 2
    
    if x1 - x0 < min_w:
        center_x = (x0 + x1) // 2
        x0 = max(0, center_x - min_w // 2)
        x1 = min(w, x0 + min_w)
    elif x1 - x0 > max_w:
        center_x = (x0 + x1) // 2
        x0 = max(0, center_x - max_w // 2)
        x1 = min(w, x0 + max_w)
        
    if y1 - y0 < min_h:
        center_y = (y0 + y1) // 2
        y0 = max(0, center_y - min_h // 2)
        y1 = min(h, y0 + min_h)
    elif y1 - y0 > max_h:
        center_y = (y0 + y1) // 2
        y0 = max(0, center_y - max_h // 2)
        y1 = min(h, y0 + max_h)
    
    return int(x0), int(y0), int(x1), int(y1)


def _refine_with_grabcut(img_bgr: np.ndarray, rect, iters=3):
    """
    Optional refinement with GrabCut if OpenCV is available.
    rect: (x, y, w, h)
    Returns mask in {0,1}
    """
    if not _HAS_CV2:
        return None
    h, w = img_bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(img_bgr, mask, rect, bgdModel, fgdModel, iters, cv2.GC_INIT_WITH_RECT)
        mask_bin = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
        return mask_bin
    except Exception:
        return None


def _fit_box_to_aspect(x0, y0, x1, y1, W, H, target_aspect, padding=0.1):
    """
    Expand the box with padding and adjust to target aspect ratio while keeping center.
    Clamp to image bounds. Returns integer box [x0,y0,x1,y1).
    """
    # current box
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    cx = x0 + bw / 2
    cy = y0 + bh / 2

    # add padding
    bw *= (1.0 + padding * 2.0)
    bh *= (1.0 + padding * 2.0)

    # enforce aspect
    box_aspect = bw / bh
    if box_aspect < target_aspect:
        # too tall -> widen
        bw = bh * target_aspect
    else:
        # too wide -> heighten
        bh = bw / target_aspect

    # convert to coordinates
    nx0 = int(round(cx - bw / 2))
    ny0 = int(round(cy - bh / 2))
    nx1 = int(round(cx + bw / 2))
    ny1 = int(round(cy + bh / 2))

    # clamp to bounds, maintaining size if possible
    bw = nx1 - nx0
    bh = ny1 - ny0

    if nx0 < 0:
        nx1 = min(W, nx1 - nx0)
        nx0 = 0
    if ny0 < 0:
        ny1 = min(H, ny1 - ny0)
        ny0 = 0
    if nx1 > W:
        shift = nx1 - W
        nx0 = max(0, nx0 - shift)
        nx1 = W
    if ny1 > H:
        shift = ny1 - H
        ny0 = max(0, ny0 - shift)
        ny1 = H

    # ensure >0
    nx0 = int(np.clip(nx0, 0, W - 1))
    ny0 = int(np.clip(ny0, 0, H - 1))
    nx1 = int(np.clip(nx1, nx0 + 1, W))
    ny1 = int(np.clip(ny1, ny0 + 1, H))

    return nx0, ny0, nx1, ny1


def _resize_np(img: np.ndarray, out_w: int, out_h: int, allow_upscale=False, interpolation="lanczos"):
    h, w = img.shape[:2]
    if not allow_upscale and (out_w > w or out_h > h):
        # shrink only, keep aspect
        scale = min(out_w / w, out_h / h, 1.0)
        out_w = max(1, int(round(w * scale)))
        out_h = max(1, int(round(h * scale)))

    pil = Image.fromarray(img)
    interp_map = {
        "lanczos": Image.LANCZOS,
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "nearest": Image.NEAREST,
    }
    pil = pil.resize((out_w, out_h), interp_map.get(interpolation, Image.LANCZOS))
    return np.array(pil)


def _apply_centering_preference(x0, y0, x1, y1, W, H, target_w, target_h, centering_preference):
    """
    Apply centering preference to the crop box.
    Returns adjusted coordinates [x0,y0,x1,y1).
    """
    # Calculate current center
    current_cx = (x0 + x1) / 2
    current_cy = (y0 + y1) / 2
    
    # Calculate target center based on preference
    if centering_preference == "left":
        target_cx = target_w / 2  # Left side of image
    elif centering_preference == "right":
        target_cx = W - target_w / 2  # Right side of image
    else:  # center
        target_cx = W / 2  # Center of image
    
    target_cy = H / 2  # Always center vertically
    
    # Calculate offset needed
    offset_x = target_cx - current_cx
    offset_y = target_cy - current_cy
    
    # Apply offset
    new_x0 = max(0, int(x0 + offset_x))
    new_y0 = max(0, int(y0 + offset_y))
    new_x1 = min(W, int(x1 + offset_x))
    new_y1 = min(H, int(y1 + offset_y))
    
    # Ensure minimum size
    if new_x1 - new_x0 < 1:
        new_x1 = min(W, new_x0 + 1)
    if new_y1 - new_y0 < 1:
        new_y1 = min(H, new_y0 + 1)
    
    return new_x0, new_y0, new_x1, new_y1


def _draw_poi_overlay(img: np.ndarray, x0: int, y0: int, x1: int, y1: int, color=(255, 0, 0), thickness=2):
    """
    Draw a rectangle overlay on the image to show the POI detection box.
    Returns a copy of the image with the overlay drawn.
    """
    overlay_img = img.copy()
    h, w = overlay_img.shape[:2]
    
    # Ensure coordinates are within bounds
    x0 = max(0, min(x0, w-1))
    y0 = max(0, min(y0, h-1))
    x1 = max(x0+1, min(x1, w))
    y1 = max(y0+1, min(y1, h))
    
    # Draw rectangle outline
    if len(overlay_img.shape) == 3:
        # RGB image
        overlay_img[y0:y0+thickness, x0:x1] = color  # Top edge
        overlay_img[y1-thickness:y1, x0:x1] = color  # Bottom edge
        overlay_img[y0:y1, x0:x0+thickness] = color  # Left edge
        overlay_img[y0:y1, x1-thickness:x1] = color  # Right edge
    else:
        # Grayscale image
        overlay_img[y0:y0+thickness, x0:x1] = 255  # Top edge
        overlay_img[y1-thickness:y1, x0:x1] = 255  # Bottom edge
        overlay_img[y0:y1, x0:x0+thickness] = 255  # Left edge
        overlay_img[y0:y1, x1-thickness:x1] = 255  # Right edge
    
    return overlay_img


class POISmartCrop:
    """
    ComfyUI node: lightweight smart crop keeping point-of-interest in frame.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "width": ("INT", {"default": 1080, "min": 1, "max": 8192}),
                "height": ("INT", {"default": 1350, "min": 1, "max": 8192}),
                "interpolation": (["lanczos", "bicubic", "bilinear", "nearest"], {"default": "lanczos"}),
                "method": (["fill / crop", "fit"], {"default": "fill / crop"}),
                "condition": (["always", "if_larger", "if_smaller"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 0, "min": 0, "max": 64}),
                "centering_preference": (["left", "center", "right"], {"default": "center"}),
                "padding": ("FLOAT", {"default": 0.12, "min": 0.0, "max": 0.75, "step": 0.01}),
            },
            "optional": {
                "refine_with_grabcut": ("BOOLEAN", {"default": False}),
                "fallback_center_crop": ("BOOLEAN", {"default": True}),
                "show_overlay": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOX",)
    RETURN_NAMES = ("cropped", "box_xyxy")
    FUNCTION = "run"
    CATEGORY = "image/transform"

    def run(
        self,
        images: torch.Tensor,
        width: int,
        height: int,
        interpolation: str = "lanczos",
        method: str = "fill / crop",
        condition: str = "always",
        multiple_of: int = 0,
        centering_preference: str = "center",
        padding: float = 0.12,
        refine_with_grabcut: bool = False,
        fallback_center_crop: bool = True,
        show_overlay: bool = False,
    ):
        """
        images: torch tensor [B,H,W,C], 0..1
        returns cropped images (batch preserved) and last crop box (x0,y0,x1,y1).
        """
        assert images.dim() == 4, "Expected [B,H,W,C] tensor"
        B, H, W, C = images.shape
        target_aspect = max(1e-6, float(width) / float(height))
        
        # Handle optional parameters (they might be None if not connected)
        refine_with_grabcut_bool = refine_with_grabcut if refine_with_grabcut is not None else False
        fallback_center_crop_bool = fallback_center_crop if fallback_center_crop is not None else True
        show_overlay_bool = show_overlay if show_overlay is not None else False

        # Apply multiple_of constraint if specified
        if multiple_of > 0:
            width = ((width + multiple_of - 1) // multiple_of) * multiple_of
            height = ((height + multiple_of - 1) // multiple_of) * multiple_of

        out_list = []
        last_box = (0, 0, W, H)

        for b in range(B):
            frame = images[b]  # [H,W,C]
            np_img = _to_uint8(frame)
            h, w = np_img.shape[:2]

            # Check condition for resizing
            should_resize = True
            if condition == "if_larger":
                should_resize = width < w or height < h
            elif condition == "if_smaller":
                should_resize = width > w or height > h

            if not should_resize:
                # Return original image if condition not met
                out_list.append(_to_tensor(np_img))
                last_box = (0, 0, w, h)
                continue

            # grayscale
            gray = np_img
            if gray.shape[2] == 3:
                gray = np.dot(gray[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = gray[..., 0]

            # saliency
            S = spectral_residual_saliency(gray)
            
            # Check if saliency is too uniform (indicating poor detection)
            saliency_std = np.std(S)
            saliency_range = np.max(S) - np.min(S)
            
            # If saliency is too uniform, try edge-based fallback
            if saliency_std < 0.01 or saliency_range < 0.1:
                if _HAS_CV2:
                    # Use edge detection as fallback
                    edges = cv2.Canny(gray, 50, 150)
                    # Convert edges to saliency-like map
                    S = edges.astype(np.float32) / 255.0
                    # Apply gaussian blur to make it more like saliency
                    S = cv2.GaussianBlur(S, (15, 15), 0)
                    S = S / (S.max() + 1e-8)
                else:
                    # Simple gradient-based fallback
                    from scipy.ndimage import sobel
                    S = np.sqrt(sobel(gray, axis=0)**2 + sobel(gray, axis=1)**2)
                    S = S / (S.max() + 1e-8)

            # optional GrabCut refinement
            if refine_with_grabcut_bool and _HAS_CV2:
                x0_s, y0_s, x1_s, y1_s = _compute_median_box_from_saliency(S)
                rect = (x0_s, y0_s, max(1, x1_s - x0_s), max(1, y1_s - y0_s))
                gc_mask = _refine_with_grabcut(cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR), rect)
                if gc_mask is not None:
                    S = (gc_mask.astype(np.float32))
                    if S.max() > 0:
                        S = S / S.max()

            # Dynamic automated box computation
            x0, y0, x1, y1 = _compute_median_box_from_saliency(S)

            # if saliency is too flat, optionally fallback to center crop
            if float(S.sum()) < 1e-6 and fallback_center_crop_bool:
                # center box with aspect
                if w / h < target_aspect:
                    # image narrower than target -> height drives
                    bw = w
                    bh = int(round(w / target_aspect))
                else:
                    bh = h
                    bw = int(round(h * target_aspect))
                cx = w // 2
                cy = h // 2
                x0 = max(0, cx - bw // 2)
                x1 = min(w, x0 + bw)
                y0 = max(0, cy - bh // 2)
                y1 = min(h, y0 + bh)

            # adjust to target aspect and clamp
            x0, y0, x1, y1 = _fit_box_to_aspect(x0, y0, x1, y1, w, h, target_aspect, padding=padding)
            
            # Apply centering preference
            x0, y0, x1, y1 = _apply_centering_preference(x0, y0, x1, y1, w, h, width, height, centering_preference)
            
            last_box = (int(x0), int(y0), int(x1), int(y1))

            # crop
            crop = np_img[y0:y1, x0:x1, :]
            
            # Apply debug overlay if enabled
            if show_overlay_bool:
                # Draw overlay on the original image to show POI detection
                debug_img = _draw_poi_overlay(np_img, x0, y0, x1, y1, color=(255, 0, 0), thickness=3)
                # Also draw on the crop to show the final result
                crop = _draw_poi_overlay(crop, 0, 0, crop.shape[1], crop.shape[0], color=(0, 255, 0), thickness=2)

            # Apply resize method - always maintain aspect ratio
            crop_h, crop_w = crop.shape[:2]
            
            if method == "fit":
                # Fit the crop to target dimensions while maintaining aspect ratio
                # Scale down to fit within target dimensions
                scale = min(width / crop_w, height / crop_h)
                new_w = int(crop_w * scale)
                new_h = int(crop_h * scale)
                crop = _resize_np(crop, new_w, new_h, allow_upscale=True, interpolation=interpolation)
            else:  # "fill / crop" - default behavior
                # Scale to fill target dimensions, maintaining aspect ratio
                # This may result in dimensions larger than target, which will be cropped
                scale = max(width / crop_w, height / crop_h)
                new_w = int(crop_w * scale)
                new_h = int(crop_h * scale)
                crop = _resize_np(crop, new_w, new_h, allow_upscale=True, interpolation=interpolation)
                
                # If the scaled image is larger than target, center crop to target size
                if new_w > width or new_h > height:
                    # Calculate crop coordinates to center the image
                    start_x = max(0, (new_w - width) // 2)
                    start_y = max(0, (new_h - height) // 2)
                    crop = crop[start_y:start_y + height, start_x:start_x + width]

            out_list.append(_to_tensor(crop))

        # stack back to [B,h,w,c]
        max_h = max(im.shape[0] for im in out_list)
        max_w = max(im.shape[1] for im in out_list)

        # Pad to the max in batch so shapes match (Comfy prefers consistent batch tensor)
        padded = []
        for im in out_list:
            h2, w2, _ = im.shape
            canvas = torch.zeros((max_h, max_w, im.shape[2]), dtype=im.dtype)
            canvas[:h2, :w2, :] = im
            padded.append(canvas)
        out_tensor = torch.stack(padded, dim=0)

        # BOX type is a tuple; ComfyUI can pass it around to other nodes if needed
        return (out_tensor, last_box)


NODE_CLASS_MAPPINGS = {
    "POISmartCrop": POISmartCrop,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "POISmartCrop": "POI Smart Crop (Enhanced)",
}
