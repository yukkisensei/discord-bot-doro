"""
Ultra Beautiful Profile Card Generator for Doro Bot v2
Premium design with gradients and modern effects
"""

import os
import io
import random
import aiohttp
import math
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import hashlib
from datetime import datetime, timedelta

class ProfileCard:
    """Enhanced profile card generator with ultra-modern design"""
    
    def __init__(self):
        self.width = 900
        self.height = 500
        # No NASA - just use generated backgrounds
        
        # Load fonts - use Windows system fonts that ACTUALLY exist
        try:
            # Windows always has these fonts
            font_paths = [
                "C:/Windows/Fonts/segoeui.ttf",     # Segoe UI - modern Windows font
                "C:/Windows/Fonts/Arial.ttf",       # Arial - universal fallback
                "C:/Windows/Fonts/calibri.ttf",     # Calibri
                "arial.ttf",                         # System font name
            ]
            
            font_file = None
            for path in font_paths:
                try:
                    # Try to load the font to verify it works
                    test_font = ImageFont.truetype(path, 12)
                    font_file = path
                    print(f"✅ Using font: {path}")
                    break
                except:
                    continue
            
            if font_file:
                self.font_xlarge = ImageFont.truetype(font_file, 38)
                self.font_large = ImageFont.truetype(font_file, 32)
                self.font_medium = ImageFont.truetype(font_file, 24)
                self.font_small = ImageFont.truetype(font_file, 18)
                self.font_tiny = ImageFont.truetype(font_file, 14)
            else:
                # If all fails, use PIL default
                print("⚠️ Using PIL default font")
                self.font_xlarge = ImageFont.load_default()
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
                self.font_tiny = ImageFont.load_default()
        except Exception as e:
            print(f"❌ Font loading error: {e}")
            self.font_xlarge = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_tiny = ImageFont.load_default()
    
    async def download_avatar(self, url: str) -> Optional[Image.Image]:
        """Download avatar from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return Image.open(io.BytesIO(data))
        except:
            return None
    
    
    def create_starry_sky_background(self, level: int) -> Image.Image:
        """Create polished starry sky background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        # Sky gradient colours
        if level >= 100:
            top_color = (16, 4, 35)
            mid_color = (71, 13, 98)
            bottom_color = (149, 38, 143)
        elif level >= 50:
            top_color = (12, 23, 54)
            mid_color = (78, 53, 151)
            bottom_color = (255, 140, 90)
        elif level >= 25:
            top_color = (8, 18, 46)
            mid_color = (24, 56, 120)
            bottom_color = (64, 120, 200)
        else:
            top_color = (20, 42, 110)
            mid_color = (60, 110, 190)
            bottom_color = (120, 180, 230)

        # Gradient fill (top -> mid -> bottom)
        for y in range(self.height):
            t = y / self.height
            if t < 0.55:
                local = t / 0.55
                r = int(top_color[0] + (mid_color[0] - top_color[0]) * local)
                g = int(top_color[1] + (mid_color[1] - top_color[1]) * local)
                b = int(top_color[2] + (mid_color[2] - top_color[2]) * local)
            else:
                local = (t - 0.55) / 0.45
                r = int(mid_color[0] + (bottom_color[0] - mid_color[0]) * local)
                g = int(mid_color[1] + (bottom_color[1] - mid_color[1]) * local)
                b = int(mid_color[2] + (bottom_color[2] - mid_color[2]) * local)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        star_layer = Image.new('RGBA', (self.width, self.height))
        star_draw = ImageDraw.Draw(star_layer)

        # Small distant stars
        for _ in range(350):
            x = random.randint(0, self.width)
            y = random.randint(0, int(self.height * 0.75))
            brightness = random.randint(180, 255)
            star_draw.point((x, y), fill=(brightness, brightness, brightness, 220))

        # Medium stars with glow
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, int(self.height * 0.8))
            brightness = random.randint(200, 255)
            size = random.choice([1, 1, 2])
            star_draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=(brightness, brightness, brightness, 255))
            star_draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=(brightness, brightness, brightness, 60))

        # Bright focal stars
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, int(self.height * 0.6))
            for radius, alpha in [(6, 35), (4, 80), (2, 255)]:
                star_draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=(255, 255, 240, alpha))

        # Shooting stars for higher levels
        if level >= 40:
            for _ in range(2):
                x = random.randint(60, self.width - 140)
                y = random.randint(40, int(self.height * 0.4))
                length = random.randint(70, 120)
                for i in range(length):
                    alpha = max(0, 220 - i * 3)
                    star_draw.line([(x+i, y+i//3), (x+i+1, y+i//3)], fill=(255, 255, 255, alpha))

        # Nebula clouds for high levels
        if level >= 80:
            nebula = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            nebula_draw = ImageDraw.Draw(nebula)
            for _ in range(3):
                cx = random.randint(120, self.width-120)
                cy = random.randint(80, int(self.height * 0.5))
                max_r = random.randint(90, 150)
                color = random.choice([(160, 70, 255, 50), (255, 110, 220, 45), (90, 180, 255, 45)])
                for radius in range(max_r, 0, -6):
                    alpha = int(color[3] * (radius / max_r))
                    nebula_draw.ellipse([(cx-radius, cy-radius), (cx+radius, cy+radius)], fill=(color[0], color[1], color[2], alpha))
            star_layer = Image.alpha_composite(star_layer, nebula)

        img = Image.alpha_composite(img.convert('RGBA'), star_layer).convert('RGB')
        return img
    
    def draw_modern_stat_card(self, draw, x, y, w, h, icon_text, label, value, primary_color, secondary_color):
        """Draw glassmorphism stat card"""
        # Base glass panel
        draw.rounded_rectangle(
            [(x, y), (x+w, y+h)],
            radius=15,
            fill=(20, 20, 35, 160),
            outline=(*primary_color, 100),
            width=1
        )

        # Accent bar
        draw.rounded_rectangle(
            [(x, y), (x+12, y+h)],
            radius=20,
            fill=primary_color + (180,)
        )

        # Icon circle
        icon_radius = 20
        icon_center = (x + 40, y + h // 2)
        draw.ellipse(
            [(icon_center[0]-icon_radius, icon_center[1]-icon_radius),
             (icon_center[0]+icon_radius, icon_center[1]+icon_radius)],
            fill=secondary_color + (200,)
        )

        # Icon text
        icon_bbox = draw.textbbox((0, 0), icon_text, font=self.font_small)
        icon_w = icon_bbox[2] - icon_bbox[0]
        icon_h = icon_bbox[3] - icon_bbox[1]
        draw.text(
            (icon_center[0] - icon_w//2, icon_center[1] - icon_h//2 - 1),
            icon_text,
            fill=(15, 20, 35),
            font=self.font_small
        )

        # Label and value
        draw.text((x+75, y+10), label, fill=(200, 205, 215), font=self.font_tiny)
        draw.text((x+75, y+30), str(value), fill=(250, 250, 255), font=self.font_medium)
    
    async def generate_profile_card(
        self,
        username: str,
        avatar_url: str,
        level: int,
        xp: int,
        xp_needed: int,
        balance: int,
        bank: int,
        streak: int,
        wins: int,
        losses: int,
        is_infinity: bool = False,
        equipped_ring: str = None,
        equipped_pet: str = None,
        partner_name: str = None
    ) -> io.BytesIO:
        """Generate ultra-beautiful profile card"""
        
        # Use generated starry sky background (no more NASA!)
        bg = self.create_starry_sky_background(level)
        
        img = bg.convert('RGBA')
        draw = ImageDraw.Draw(img)

        # Palette selections per tier (muted luxe tone)
        if is_infinity:
            palette = {
                "primary": (255, 214, 140),
                "secondary": (255, 236, 185),
                "accent": (250, 247, 240),
                "header_panel": (18, 25, 54, 200),
                "ring": (255, 222, 120),
                "text": (250, 247, 240),
                "badge": (255, 224, 153)
            }
        elif level >= 100:
            palette = {
                "primary": (176, 136, 255),
                "secondary": (229, 194, 255),
                "accent": (242, 238, 255),
                "header_panel": (18, 25, 54, 200),
                "ring": (171, 129, 255),
                "text": (240, 238, 255),
                "badge": (198, 160, 255)
            }
        elif level >= 50:
            palette = {
                "primary": (255, 182, 116),
                "secondary": (255, 215, 170),
                "accent": (255, 245, 233),
                "header_panel": (20, 30, 60, 200),
                "ring": (255, 194, 140),
                "text": (255, 247, 239),
                "badge": (255, 204, 150)
            }
        elif level >= 25:
            palette = {
                "primary": (114, 188, 255),
                "secondary": (176, 220, 255),
                "accent": (236, 246, 255),
                "header_panel": (18, 32, 70, 200),
                "ring": (134, 200, 255),
                "text": (235, 245, 255),
                "badge": (164, 210, 255)
            }
        else:
            palette = {
                "primary": (148, 222, 185),
                "secondary": (198, 244, 215),
                "accent": (240, 252, 244),
                "header_panel": (18, 40, 70, 200),
                "ring": (168, 236, 205),
                "text": (240, 250, 245),
                "badge": (188, 240, 212)
            }

        primary_color = palette["primary"]
        secondary_color = palette["secondary"]
        accent_color = palette["accent"]
        text_color = palette["text"]
        
        # Avatar section with premium effects
        avatar = await self.download_avatar(avatar_url)
        if avatar:
            avatar_size = 140
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # Avatar position - moved down to avoid overlap
            avatar_x, avatar_y = 50, 80
            
            # Draw animated ring effect
            for i in range(15, 0, -1):
                ring_alpha = 12 * i
                ring_size = avatar_size + i*4
                draw.ellipse(
                    [(avatar_x-i*2, avatar_y-i*2),
                     (avatar_x+ring_size-avatar_size//2+i*2, avatar_y+ring_size-avatar_size//2+i*2)],
                    outline=(*primary_color, ring_alpha),
                    width=2
                )
            
            # Paste avatar
            output = Image.new('RGBA', avatar.size, (0, 0, 0, 0))
            output.paste(avatar, (0, 0))
            output.putalpha(mask)
            img.paste(output, (avatar_x, avatar_y), output)
        
        draw = ImageDraw.Draw(img)
        
        # Username with shadow - adjusted position
        # Handle username display - keep as much as possible
        # Arial/Segoe can handle most Latin chars but not emoji
        # Strategy: Try to display the username, use fallback if it's all emoji
        import re
        
        # First, try to keep alphanumeric and common symbols
        # Remove only emoji and special unicode that Arial can't render
        clean_username = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+', '', username)
        
        # If after removing emoji, we still have text, use it
        if clean_username.strip():
            # Keep Latin chars, numbers, spaces, and common punctuation
            clean_username = clean_username.strip()
        else:
            # Username is all emoji/special chars, use fallback
            clean_username = "User"
        
        username_x = 220
        username_y = 90
        # Multiple shadow layers for depth
        for i in range(3, 0, -1):
            draw.text(
                (username_x+i, username_y+i),
                clean_username,
                fill=(0, 0, 0, 100),
                font=self.font_xlarge
            )
        draw.text((username_x, username_y), clean_username, fill=text_color, font=self.font_xlarge)
        
        # Level badge - pill style
        level_text = "INFINITY" if is_infinity else f"Lv {level}"
        badge_x = 220
        badge_y = 140
        badge_width = 200
        badge_height = 44

        # Background blur/glass panel behind username & badge
        panel = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        panel_draw = ImageDraw.Draw(panel)
        panel_draw.rounded_rectangle(
            [(180, 70), (820, 200)],
            radius=30,
            fill=(15, 15, 35, 140)
        )
        img = Image.alpha_composite(img, panel)
        draw = ImageDraw.Draw(img)

        # Level pill with light gradient
        badge_gradient = Image.new('RGBA', (badge_width, badge_height), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(badge_gradient)
        for i in range(badge_height):
            ratio = i / badge_height
            r = int(primary_color[0] + (secondary_color[0] - primary_color[0]) * ratio)
            g = int(primary_color[1] + (secondary_color[1] - primary_color[1]) * ratio)
            b = int(primary_color[2] + (secondary_color[2] - primary_color[2]) * ratio)
            grad_draw.line([(0, i), (badge_width, i)], fill=(r, g, b, 220))
        badge_gradient = badge_gradient.filter(ImageFilter.GaussianBlur(radius=0.8))
        img.paste(badge_gradient, (badge_x, badge_y), badge_gradient)

        # Level text centered
        level_bbox = draw.textbbox((0, 0), level_text, font=self.font_medium)
        level_w = level_bbox[2] - level_bbox[0]
        level_h = level_bbox[3] - level_bbox[1]
        draw.text(
            (badge_x + (badge_width - level_w) // 2, badge_y + (badge_height - level_h) // 2),
            level_text,
            fill=(22, 24, 36),
            font=self.font_medium
        )
        
        # XP Progress Bar (animated style)
        if not is_infinity:
            bar_x = 210
            bar_y = 210
            bar_width = 640
            bar_height = 20
            
            # Bar background
            draw.rounded_rectangle(
                [(bar_x, bar_y), (bar_x+bar_width, bar_y+bar_height)],
                radius=10,
                fill=(20, 20, 30, 200)
            )
            
            # Progress
            progress = min(xp / xp_needed, 1.0)
            progress_width = int(bar_width * progress)
            
            if progress_width > 0:
                # Gradient progress bar
                for i in range(progress_width):
                    ratio = i / progress_width
                    r = int(primary_color[0] + (secondary_color[0] - primary_color[0]) * ratio)
                    g = int(primary_color[1] + (secondary_color[1] - primary_color[1]) * ratio)
                    b = int(primary_color[2] + (secondary_color[2] - primary_color[2]) * ratio)
                    draw.line(
                        [(bar_x+i, bar_y), (bar_x+i, bar_y+bar_height)],
                        fill=(r, g, b)
                    )
                
                # Shine effect on progress bar
                shine_width = 30
                for i in range(min(shine_width, progress_width)):
                    alpha = int(100 * (1 - i/shine_width))
                    x = bar_x + progress_width - shine_width + i
                    if x >= bar_x:
                        draw.line(
                            [(x, bar_y), (x, bar_y+bar_height)],
                            fill=(255, 255, 255, alpha)
                        )
            
            # XP text
            xp_text = f"{xp:,} / {xp_needed:,} XP"
            draw.text((bar_x, bar_y - 22), xp_text, fill=accent_color, font=self.font_small)
            
            # Percentage
            pct_text = f"{int(progress * 100)}%"
            pct_bbox = draw.textbbox((0, 0), pct_text, font=self.font_tiny)
            pct_w = pct_bbox[2] - pct_bbox[0]
            draw.text(
                (bar_x + bar_width - pct_w, bar_y - 22),
                pct_text,
                fill=(180, 180, 190),
                font=self.font_tiny
            )
        
        # Stats layout - floating cards (moved down for better spacing)
        stats_y = 370
        card_width = 185
        card_height = 75
        card_spacing = 20

        total_width = card_width * 4 + card_spacing * 3
        start_x = (self.width - total_width) // 2

        stat_colors = [
            ((238, 198, 126), (255, 225, 166)),
            ((134, 188, 255), (182, 220, 255)),
            ((255, 166, 175), (255, 206, 206)),
            ((156, 228, 196), (200, 246, 220))
        ]

        balance_text = "INFINITY" if is_infinity else f"${balance:,}"
        self.draw_modern_stat_card(
            draw, start_x, stats_y, card_width, card_height,
            "$", "WALLET", balance_text,
            stat_colors[0][0], stat_colors[0][1]
        )

        bank_text = "INFINITY" if is_infinity else f"${bank:,}"
        self.draw_modern_stat_card(
            draw, start_x + (card_width + card_spacing), stats_y, card_width, card_height,
            "B", "BANK", bank_text,
            stat_colors[1][0], stat_colors[1][1]
        )

        self.draw_modern_stat_card(
            draw, start_x + 2 * (card_width + card_spacing), stats_y, card_width, card_height,
            "S", "STREAK", f"{streak} ngày",
            stat_colors[2][0], stat_colors[2][1]
        )

        # Calculate win rate - 100% for infinity users
        if is_infinity:
            win_rate = 100.0
        else:
            total_games = wins + losses
            if total_games > 0:
                win_rate = (wins / total_games) * 100
            else:
                win_rate = 0
        win_primary = stat_colors[3][0] if win_rate >= 50 else (255, 184, 150)
        win_secondary = stat_colors[3][1] if win_rate >= 50 else (255, 217, 196)
        self.draw_modern_stat_card(
            draw, start_x + 3 * (card_width + card_spacing), stats_y, card_width, card_height,
            "%", "TỈ LỆ THẮNG", f"{win_rate:.1f}%",
            win_primary, win_secondary
        )
        
        # Footer with style (moved down to avoid overlap with stats)
        footer_y = 460
        
        # Equipped items (if any)
        if partner_name or equipped_ring or equipped_pet:
            # Items background
            draw.rounded_rectangle(
                [(40, footer_y), (860, footer_y+50)],
                radius=15,
                fill=(20, 20, 30, 180)
            )
            
            item_x = 60
            if partner_name:
                draw.ellipse([(item_x, footer_y+10), (item_x+30, footer_y+40)], fill=(255, 105, 180))
                draw.ellipse([(item_x+5, footer_y+15), (item_x+25, footer_y+35)], fill=(20, 20, 30))
                draw.text((item_x+10, footer_y+15), "P", fill=(255, 255, 255), font=self.font_small)
                draw.text((item_x+40, footer_y+15), partner_name[:20], fill=(255, 182, 193), font=self.font_small)
                item_x += 250
            
            if equipped_ring:
                draw.ellipse([(item_x, footer_y+10), (item_x+30, footer_y+40)], fill=(255, 215, 0))
                draw.ellipse([(item_x+5, footer_y+15), (item_x+25, footer_y+35)], fill=(20, 20, 30))
                draw.text((item_x+10, footer_y+15), "R", fill=(255, 255, 255), font=self.font_small)
                draw.text((item_x+40, footer_y+15), equipped_ring[:20], fill=(255, 215, 0), font=self.font_small)
                item_x += 250
            
            if equipped_pet:
                draw.ellipse([(item_x, footer_y+10), (item_x+30, footer_y+40)], fill=(100, 200, 255))
                draw.ellipse([(item_x+5, footer_y+15), (item_x+25, footer_y+35)], fill=(20, 20, 30))
                draw.text((item_x+10, footer_y+15), "T", fill=(255, 255, 255), font=self.font_small)
                draw.text((item_x+40, footer_y+15), equipped_pet[:20], fill=(100, 200, 255), font=self.font_small)
            
            footer_y += 60
        
        # Special badge for high levels
        if is_infinity or level >= 25:
            badge_x = 750
            badge_y = 150
            
            if is_infinity:
                badge_text = "INFINITY"
                badge_color = (255, 215, 0)
            elif level >= 100:
                badge_text = "COSMIC"
                badge_color = (138, 43, 226)
            elif level >= 50:
                badge_text = "LEGEND"
                badge_color = (255, 140, 0)
            else:
                badge_text = "VETERAN"
                badge_color = (0, 191, 255)
            
            # Badge with glow
            for i in range(5, 0, -1):
                draw.ellipse(
                    [(badge_x-i*3, badge_y-i*3), (badge_x+60+i*3, badge_y+60+i*3)],
                    outline=(*badge_color, 50*i),
                    width=2
                )
            
            draw.ellipse([(badge_x, badge_y), (badge_x+60, badge_y+60)], fill=badge_color)
            draw.ellipse([(badge_x+5, badge_y+5), (badge_x+55, badge_y+55)], fill=(20, 20, 30))
            
            # Badge text
            badge_bbox = draw.textbbox((0, 0), badge_text[0], font=self.font_large)
            badge_w = badge_bbox[2] - badge_bbox[0]
            draw.text(
                (badge_x + 30 - badge_w//2, badge_y + 15),
                badge_text[0],
                fill=(255, 255, 255),
                font=self.font_large
            )
        
        # Footer text
        draw.text((40, footer_y), "Doro Bot Profile", fill=(150, 150, 160), font=self.font_tiny)
        draw.text((self.width - 80, footer_y), "v3.0", fill=(150, 150, 160), font=self.font_tiny)
        
        # Save to BytesIO
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True, quality=95)
        output.seek(0)
        
        return output

# Global instance
profile_card_generator = ProfileCard()
