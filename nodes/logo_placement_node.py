import torch
import torch.nn.functional as F

class APZmediaLogoPlacement:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "background_image": ("IMAGE", {}),
                "logo_image": ("IMAGE", {}),
                "logo_mask": ("IMAGE", {}),
                "position": ("STRING", {"choices": [
                    "top-left", "top-center", "top-right",
                    "center-left", "center", "center-right",
                    "bottom-left", "bottom-center", "bottom-right"
                ]}),
                "scale": ("FLOAT", {"default": 0.2, "min": 0.01, "max": 1.0, "step": 0.01}),
                "offset_x": ("INT", {"default": 0}),
                "offset_y": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("composited_image",)

    FUNCTION = "place_logo"

    CATEGORY = "apzmedia_brand"

    def place_logo(self, background_image, logo_image, logo_mask, position, scale, offset_x, offset_y):
        bg = background_image.clone()
        logo = logo_image.clone()
        mask = logo_mask.clone()

        bg_h, bg_w = bg.shape[1], bg.shape[2]

        # Scale logo
        new_w = int(bg_w * scale)
        aspect_ratio = logo.shape[1] / logo.shape[2]
        new_h = int(new_w * aspect_ratio)

        logo = F.interpolate(logo.unsqueeze(0), size=(new_h, new_w), mode="bilinear", align_corners=False).squeeze(0)
        mask = F.interpolate(mask.unsqueeze(0), size=(new_h, new_w), mode="bilinear", align_corners=False).squeeze(0)

        # Calculate position
        x, y = self.calculate_position(position, bg_w, bg_h, new_w, new_h)

        x += offset_x
        y += offset_y

        # Clamp to boundaries
        x = max(0, min(x, bg_w - new_w))
        y = max(0, min(y, bg_h - new_h))

        # Blend logo into background
        mask = mask.unsqueeze(0) if mask.dim() == 2 else mask
        if mask.shape[0] == 1:
            mask = mask.repeat(3, 1, 1)

        logo = logo[:, :new_h, :new_w]
        mask = mask[:, :new_h, :new_w]

        bg[:, y:y+new_h, x:x+new_w] = (logo * mask) + (bg[:, y:y+new_h, x:x+new_w] * (1 - mask))

        return (bg,)

    def calculate_position(self, position, bg_w, bg_h, logo_w, logo_h):
        positions = {
            "top-left": (0, 0),
            "top-center": ((bg_w - logo_w) // 2, 0),
            "top-right": (bg_w - logo_w, 0),
            "center-left": (0, (bg_h - logo_h) // 2),
            "center": ((bg_w - logo_w) // 2, (bg_h - logo_h) // 2),
            "center-right": (bg_w - logo_w, (bg_h - logo_h) // 2),
            "bottom-left": (0, bg_h - logo_h),
            "bottom-center": ((bg_w - logo_w) // 2, bg_h - logo_h),
            "bottom-right": (bg_w - logo_w, bg_h - logo_h),
        }
        return positions.get(position, (0, 0))

NODE_CLASS_MAPPINGS = {
    "APZmediaLogoPlacement": APZmediaLogoPlacement,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaLogoPlacement": "APZmedia - Logo Placement",
}
