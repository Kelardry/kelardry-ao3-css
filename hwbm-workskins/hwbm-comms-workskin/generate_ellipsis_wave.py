"""
Generate ellipsis APNG with CORRECT wave animation:
- Wave of fading: dots fade left to right
- All dots reach minimum
- Wave of brightening: dots brighten left to right
- Loop

Can change output filename with a command line argument
Change image attributes by manually changing in the animation parameters section at top of file.

Pattern:
0.00s: [1.0, 1.0, 1.0] - all at max
0.25s: [0.5, 1.0, 1.0] - dot 0 fades instantly
0.50s: [0.5, 0.5, 1.0] - dot 1 fades instantly
0.75s: [0.5, 0.5, 0.5] - all at minimum
1.00s: [1.0, 0.5, 0.5] - dot 0 brightens instantly
1.25s: [1.0, 1.0, 0.5] - dot 1 brightens instantly  
1.50s: [1.0, 1.0, 1.0] - all at max, loop
"""

from PIL import Image, ImageDraw
from apng import APNG
import os

# Animation parameters
DOT_SIZE = 30 #Diameter of dot
DOT_SPACING = 26 #2px more than desired distance between the dots in px
FPS = 30
CYCLE_DURATION = 1.5  # Total animation cycle

# Timing for wave effect
FADE_START = [0.0, 0.25, 0.5]      # When each dot starts fading
BRIGHTEN_START = [0.75, 1.0, 1.25] # When each dot starts brightening
TRANSITION_TIME = 0.1  # How fast each dot transitions (fast for "instant" effect)

# Dimensions
NUM_DOTS = 3
TOTAL_WIDTH = (DOT_SIZE * NUM_DOTS) + (DOT_SPACING * (NUM_DOTS - 1))
PADDING = 2
WIDTH = TOTAL_WIDTH + (PADDING * 2)
HEIGHT = DOT_SIZE + (PADDING * 2)
TOTAL_FRAMES = int(CYCLE_DURATION * FPS)

def get_opacity_at_time(dot_index, current_time):
    """
    Get opacity for a dot at given time
    Each dot: starts at 1.0, fades to 0.5 at its fade time, 
    stays at 0.5, then brightens back to 1.0 at its brighten time
    """
    fade_time = FADE_START[dot_index]
    brighten_time = BRIGHTEN_START[dot_index]
    
    # Before fade: stay at 1.0
    if current_time < fade_time:
        return 1.0
    
    # During fade transition
    if current_time < fade_time + TRANSITION_TIME:
        progress = (current_time - fade_time) / TRANSITION_TIME
        return 1.0 - (0.5 * progress)  # 1.0 -> 0.5
    
    # Between fade and brighten: stay at 0.5
    if current_time < brighten_time:
        return 0.5
    
    # During brighten transition
    if current_time < brighten_time + TRANSITION_TIME:
        progress = (current_time - brighten_time) / TRANSITION_TIME
        return 0.5 + (0.5 * progress)  # 0.5 -> 1.0
    
    # After brighten: stay at 1.0
    return 1.0

def create_frame(frame_num):
    """Create frame with proper alpha transparency"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    current_time = (frame_num / FPS) % CYCLE_DURATION
    
    for i in range(NUM_DOTS):
        x = PADDING + (i * (DOT_SIZE + DOT_SPACING))
        y = PADDING
        
        opacity = get_opacity_at_time(i, current_time)
        alpha = int(opacity * 255)
        
        draw.ellipse(
            [x, y, x + DOT_SIZE, y + DOT_SIZE],
            fill=(0, 0, 0, alpha)
        )
    
    return img

def generate_apng(output_path='ellipsis_animation.png'):
    """Generate APNG with wave animation"""
    print(f"Generating APNG with WAVE animation")
    print(f"Frames: {TOTAL_FRAMES} at {FPS} fps")
    print(f"Duration: {CYCLE_DURATION}s")
    print(f"Size: {WIDTH}x{HEIGHT}px")
    print(f"\nAnimation pattern:")
    print(f"  0.00-0.75s: Dots fade left to right")
    print(f"  0.75s: All dots at minimum (0.5)")
    print(f"  0.75-1.50s: Dots brighten left to right")
    
    frame_files = []
    
    for i in range(TOTAL_FRAMES):
        if i % 15 == 0:
            print(f"  Frame {i}/{TOTAL_FRAMES}")
        
        frame = create_frame(i)
        temp_path = f'tmp\\frame_{i:04d}.png'
        frame.save(temp_path, 'PNG')
        frame_files.append(temp_path)
    
    # Show key moments
    print("\nKey moments:")
    key_times = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
    print("Time  | Dot 0 | Dot 1 | Dot 2 | Description")
    print("------|-------|-------|-------|-------------")
    for t in key_times:
        opacities = [get_opacity_at_time(i, t) for i in range(NUM_DOTS)]
        desc = ""
        if t == 0.0:
            desc = "All at max"
        elif t == 0.25:
            desc = "Dot 0 faded"
        elif t == 0.5:
            desc = "Dot 1 faded"
        elif t == 0.75:
            desc = "All at min"
        elif t == 1.0:
            desc = "Dot 0 brightened"
        elif t == 1.25:
            desc = "Dot 1 brightened"
        elif t == 1.5:
            desc = "All at max (loop)"
        print(f"{t:.2f}s | {opacities[0]:.2f}  | {opacities[1]:.2f}  | {opacities[2]:.2f}  | {desc}")
    
    print("\nCreating APNG...")
    apng_obj = APNG()
    frame_duration = int(1000 / FPS)
    
    for frame_path in frame_files:
        apng_obj.append_file(frame_path, delay=frame_duration)
    
    apng_obj.save(output_path)
    
    print(f"✓ Saved to {output_path}")
    
    import os
    file_size = os.path.getsize(output_path)
    print(f"  File size: {file_size / 1024:.1f} KB")
    
    # Cleanup
    for f in frame_files:
        os.remove(f)
    
    print("\nNo JavaScript needed for AO3!")
    print("Just use in CSS:")
    print("  background-image: url('ellipsis_animation.png');")

if __name__ == '__main__':
    import sys
    os.makedirs('tmp',exist_ok=True)
    output_file = 'ellipsis_animation.png'
    if len(sys.argv) > 1:
        output_file = sys.argv[1] #use command line argument for differently named output file
    
    generate_apng(output_file)
