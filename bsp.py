"""
Jonas Nockert (2020)

Binary Space partitioned tree representing social groups on overlapping levels.

"""
import math
import random
import seaborn as sns

from geometry import Rect


class BSP_Tree:

    def __init__(self, width, height):
        self.root = BSP_Node(0, 0, width, height)
        self.root.split()
        self.colormap1 = "GnBu"
        self.colormap2 = "YlOrRd"
        self.colors1 = sns.color_palette(self.colormap1, 256)
        self.colors2 = sns.color_palette(self.colormap2, 256)

    def leaves(self):
        queue = [self.root]
        leaves = []
        counter = 0
        while queue:
            node = queue.pop()
            if node.is_leaf():
                if counter % 2 == 0:
                    color = self.colors1[random.randrange(256)]
                else:
                    color = self.colors2[random.randrange(256)]
                node.color = color
                leaves.append(node)
            else:
                queue.append(node.left)
                queue.append(node.right)
            counter += 1
        return leaves

    def relative_distance(self, n1, n2):
        c1 = n1.center()
        c2 = n2.center()
        d = math.sqrt((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2)
        max_d = math.sqrt(self.root.rect.width ** 2 + self.root.rect.height ** 2)
        return d / max_d


class BSP_Node:
    MIN_SIZE = 2

    def __init__(self, x, y, width, height, level=0):
        self.left = None
        self.right = None
        self.level = level
        self.color = None
        self.rect = Rect(x, x + width - 1, y, y + height - 1)

    def is_leaf(self):
        return not self.left and not self.right

    def center(self):
        return self.rect.center

    def get_points(self):
        return self.rect.get_points()

    def split(self):
        # Already split?
        if not self.is_leaf():
            return

        split_horizontally = random.choice([True, False])
        if self.rect.ratio_wh >= 1.25:
            split_horizontally = False
        elif self.rect.ratio_hw >= 1.25:
            split_horizontally = True

        if split_horizontally:
            max_size = self.rect.height
        else:
            max_size = self.rect.width

        if max_size <= 2 * self.MIN_SIZE:
            return

        split_at = random.randint(self.MIN_SIZE, max_size - self.MIN_SIZE)
        if split_horizontally:
            # |   |
            # -----
            # |   |
            self.left = BSP_Node(
                self.rect.xmin,
                self.rect.ymin,
                self.rect.width,
                split_at,
                level=self.level + 1,
            )
            self.right = BSP_Node(
                self.rect.xmin,
                self.rect.ymin + split_at,
                self.rect.width,
                self.rect.height - split_at,
                level=self.level + 1,
            )
        else:
            # -------
            # |  |  |
            # -------
            self.left = BSP_Node(
                self.rect.xmin,
                self.rect.ymin,
                split_at,
                self.rect.height,
                level=self.level + 1,
            )
            self.right = BSP_Node(
                self.rect.xmin + split_at,
                self.rect.ymin,
                self.rect.width - split_at,
                self.rect.height,
                level=self.level + 1,
            )

        self.left.split()
        self.right.split()
