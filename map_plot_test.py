import matplotlib.pyplot as plt

UPPER_LEFT_CORNER = (42.4379, -71.3538)
LOWER_RIGHT_CORNER = (42.2059, -70.8148)

BBox = (UPPER_LEFT_CORNER[1], LOWER_RIGHT_CORNER[1],
        LOWER_RIGHT_CORNER[0], UPPER_LEFT_CORNER[0])

if __name__ == "__main__":
    boston = plt.imread("map.png")

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter([-71.09202978500981], [42.33929173531738], zorder=1, alpha=1.0, c='b', s=10)
    ax.set_title('Bike Stations')
    ax.set_xlim(BBox[0], BBox[1])
    ax.set_ylim(BBox[2], BBox[3])
    ax.imshow(boston, zorder=0, extent=BBox, aspect="auto")
    plt.show()
