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
    Lightweight saliency (Hou & Zhang 2007).
    Input gray uint8 [H,W], returns float32 saliency 0..1
    """
    # ensure float
    g = gray.astype(np.float32) / 255.0
    # FFT
    G = np.fft.fft2(g)
    A = np.abs(G)
    L = np.log(A + 1e-8)
    # average filter on log amplitude (using simple box blur)
    # small kernel is fine/fast
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
    # smooth
    from scipy.ndimage import gaussian_filter
    S = gaussian_filter(S, sigma=2.0)
    # normalize
    S -= S.min()
    if S.max() > 0:
        S /= S.max()
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
    Turns a saliency map into a robust box using weighted percentiles along axes.
    Returns (x0, y0, x1, y1) inclusive-exclusive in image coords.
    """
    # collapse to 1D distributions
    wy = S.sum(axis=1)  # per-row weights
    wx = S.sum(axis=0)  # per-col weights
    y0, y1 = _weighted_percentile_indices(wy, mass_clip[0], mass_clip[1])
    x0, x1 = _weighted_percentile_indices(wx, mass_clip[0], mass_clip[1])

    # Ensure at least 1px extent
    if x1 == x0:
        x1 = min(x0 + 1, S.shape[1] - 1)
    if y1 == y0:
        y1 = min(y0 + 1, S.shape[0] - 1)
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


class POISmartCrop:
    """
    ComfyUI node: lightweight smart crop keeping point-of-interest in frame.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "target_aspect_w": ("INT", {"default": 1, "min": 1, "max": 8192}),
                "target_aspect_h": ("INT", {"default": 1, "min": 1, "max": 8192}),
            },
            "optional": {
                "padding": ("FLOAT", {"default": 0.12, "min": 0.0, "max": 0.75, "step": 0.01}),
                "saliency_lower_pct": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 0.5, "step": 0.01}),
                "saliency_upper_pct": ("FLOAT", {"default": 0.95, "min": 0.5, "max": 1.0, "step": 0.01}),
                "refine_with_grabcut": ("BOOL", {"default": False}),
                "out_width": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "out_height": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "allow_upscale": ("BOOL", {"default": False}),
                "resize_interpolation": (["lanczos", "bicubic", "bilinear", "nearest"], {"default": "lanczos"}),
                "fallback_center_crop": ("BOOL", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOX",)
    RETURN_NAMES = ("cropped", "box_xyxy")
    FUNCTION = "run"
    CATEGORY = "image/transform"

    def run(
        self,
        images: torch.Tensor,
        target_aspect_w: int,
        target_aspect_h: int,
        padding: float = 0.12,
        saliency_lower_pct: float = 0.05,
        saliency_upper_pct: float = 0.95,
        refine_with_grabcut: bool = False,
        out_width: int = 0,
        out_height: int = 0,
        allow_upscale: bool = False,
        resize_interpolation: str = "lanczos",
        fallback_center_crop: bool = True,
    ):
        """
        images: torch tensor [B,H,W,C], 0..1
        returns cropped images (batch preserved) and last crop box (x0,y0,x1,y1).
        """
        assert images.dim() == 4, "Expected [B,H,W,C] tensor"
        B, H, W, C = images.shape
        aspect = max(1e-6, float(target_aspect_w) / float(target_aspect_h))

        out_list = []
        last_box = (0, 0, W, H)

        for b in range(B):
            frame = images[b]  # [H,W,C]
            np_img = _to_uint8(frame)
            h, w = np_img.shape[:2]

            # grayscale
            gray = np_img
            if gray.shape[2] == 3:
                gray = np.dot(gray[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = gray[..., 0]

            # saliency
            S = spectral_residual_saliency(gray)

            # optional GrabCut refinement
            if refine_with_grabcut and _HAS_CV2:
                x0_s, y0_s, x1_s, y1_s = _compute_median_box_from_saliency(
                    S, (saliency_lower_pct, saliency_upper_pct)
                )
                rect = (x0_s, y0_s, max(1, x1_s - x0_s), max(1, y1_s - y0_s))
                gc_mask = _refine_with_grabcut(cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR), rect)
                if gc_mask is not None:
                    S = (gc_mask.astype(np.float32))
                    if S.max() > 0:
                        S = S / S.max()

            # median/percentile box
            x0, y0, x1, y1 = _compute_median_box_from_saliency(
                S, (saliency_lower_pct, saliency_upper_pct)
            )

            # if saliency is too flat, optionally fallback to center crop
            if float(S.sum()) < 1e-6 and fallback_center_crop:
                # center box with aspect
                if w / h < aspect:
                    # image narrower than target -> height drives
                    bw = w
                    bh = int(round(w / aspect))
                else:
                    bh = h
                    bw = int(round(h * aspect))
                cx = w // 2
                cy = h // 2
                x0 = max(0, cx - bw // 2)
                x1 = min(w, x0 + bw)
                y0 = max(0, cy - bh // 2)
                y1 = min(h, y0 + bh)

            # adjust to target aspect and clamp
            x0, y0, x1, y1 = _fit_box_to_aspect(x0, y0, x1, y1, w, h, aspect, padding=padding)
            last_box = (int(x0), int(y0), int(x1), int(y1))

            # crop
            crop = np_img[y0:y1, x0:x1, :]

            # optional resize
            if out_width > 0 and out_height > 0:
                crop = _resize_np(
                    crop, out_width, out_height, allow_upscale=allow_upscale,
                    interpolation=resize_interpolation
                )

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
    "POISmartCrop": "POI Smart Crop (Lightweight)",
}
