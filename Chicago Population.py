import numpy as np

# AMLI.py
# Plot a linear bar graph of Chicago population by the last 10 years (Census data)
# Run: python AMLI.py

import matplotlib.pyplot as plt

def plot_chicago_population(save_path=None):
    # Years and population (Census counts by decade)
    years = np.array([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020])
    pop = np.array([3620962, 3550404, 3366957, 3005072, 2783726, 2896016, 2695598, 2746388])

    plt.figure(figsize=(8, 5))
    plt.plot(years, pop, marker='o', label='Census population', color='tab:blue')

    # Linear trend (least-squares fit)
    coeffs = np.polyfit(years, pop, 1)  # degree 1 => linear
    trend = np.poly1d(coeffs)
    plt.plot(years, trend(years), linestyle='--', color='tab:red', label=f'Linear trend\n(y = {coeffs[0]:.1f}x + {coeffs[1]:.0f})')

    plt.title('Chicago Population by Decade (1950–2020)')
    plt.xlabel('Year')
    plt.ylabel('Population')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f'Saved plot to {save_path}')
    else:
        plt.show()

if __name__ == '__main__':
    # Save to a PNG file; change to None to display interactively
    plot_chicago_population(save_path='chicago_population.png')