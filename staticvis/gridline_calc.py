# imports
from math import ceil


# main func
def main(
        pixelsize, gridlen,
        gridheight, plotbot_boo=False
):
    '''
    Uncomment the last block if you want to see the interconnecting lines between
    top and bottom grid

    Return
        line_l (list): each array in the list is of shape (points, points, points)
                       the last axis being for the height. The first few elements are
                       purely for the grid, and should be used for 2D plots
    '''
    gs = pixelsize * gridlen
    hgs = gs/2
    hps = pixelsize/2
    q, r = divmod(gridlen, 2)
    lines_l = []

    # initialise with bottom box
    if plotbot_boo:
        lines_l.append(
            [
                [-hgs, -hgs, hgs, hgs, -hgs],
                [-hgs, hgs, hgs, -hgs, -hgs],
                [0, 0, 0, 0, 0],
            ]
        )

        # grid lines
        for i in range(q):
            axdist = r*hps + i*pixelsize
            lines_l += [
                [
                    [-axdist, -axdist, axdist, axdist, -axdist],
                    [-hgs, hgs, hgs, -hgs, -hgs],
                    [0, 0, 0, 0, 0],
                ],
                [
                    [-hgs, hgs, hgs, -hgs, -hgs],
                    [-axdist, -axdist, axdist, axdist, -axdist],
                    [0, 0, 0, 0, 0],
                ]
            ]

    # top grid
    lines_l.append(
        [
            [-hgs, -hgs, hgs, hgs, -hgs],
            [-hgs, hgs, hgs, -hgs, -hgs],
            [gridheight, gridheight, gridheight, gridheight, gridheight],
        ]
    )
    for i in range(q):
        axdist = r*hps + i*pixelsize
        lines_l += [
            [
                [-axdist, -axdist, axdist, axdist, -axdist],
                [-hgs, hgs, hgs, -hgs, -hgs],
                [gridheight, gridheight, gridheight, gridheight, gridheight],
            ],
            [
                [-hgs, hgs, hgs, -hgs, -hgs],
                [-axdist, -axdist, axdist, axdist, -axdist],
                [gridheight, gridheight, gridheight, gridheight, gridheight],
            ]
        ]

    # interconnecting lines between top and bottom
    # if not r:
    #     lim = q + 1
    # else:
    #     lim = q
    # for i in range(lim):
    #     x1 = r*hps + i*pixelsize
    #     x2 = -x1
    #     for j in range(lim):
    #         y1 = r*hps + j*pixelsize
    #         y2 = -y1

    #         lines_l += [
    #             [
    #                 [x1, x1], [y1, y1], [0, gridheight],
    #             ],
    #             [
    #                 [x1, x1], [y2, y2], [0, gridheight],
    #             ],
    #             [
    #                 [x2, x2], [y1, y1], [0, gridheight],
    #             ],
    #             [
    #                 [x2, x2], [y2, y2], [0, gridheight],
    #             ],
    #         ]


    return lines_l
