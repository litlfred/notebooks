#!/usr/bin/env python3
"""
Simple script to display the test visualization
"""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def show_test_image():
    """Display the test visualization image."""
    try:
        img = mpimg.imread('test_visualization.png')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(img)
        ax.axis('off')
        ax.set_title('Weierstrass ℘ Function Test Visualization', fontsize=16)
        
        plt.tight_layout()
        plt.show()
        
        print("Test visualization displayed successfully!")
        print("This shows the two-panel layout with:")
        print("- Left panel: ℘(z) field with soft color palette")
        print("- Right panel: ℘'(z) field with soft color palette")  
        print("- Topographic contours overlaid on both panels")
        print("- Test trajectory (red line) shown on both panels")
        
    except Exception as e:
        print(f"Error displaying image: {e}")

if __name__ == "__main__":
    show_test_image()