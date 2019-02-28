#! /usr/bin/env python3

pizza = []
slices = []

popopo = []

with open('d_big.in') as f:
    lines = [line.rstrip() for line in f]
    header = lines[0]
    lines = lines[1:]

    header_split = header.split(' ') 
    min_ingredient = int(header_split[2])
    max_cells = int(header_split[3])

    n_shrooms = 0
    n_tomato = 0

    for line in lines:
        pizza.append([c for c in line])
        slices.append([0 for _ in line])
        n_shrooms += sum([c == 'M' for c in line])
        n_tomato += sum([c == 'T' for c in line])

max_row = len(pizza)
max_col = len(pizza[0])

underrepresented = 'T' if n_shrooms > n_tomato else 'M'

def find_corners(origin, points):
    rows = [point[0] for point in points + origin]
    cols = [point[1] for point in points + origin]

    return ((min(rows), min(cols)), (max(rows), max(cols)))

def other(c):
    return 'M' if c == 'T' else 'T'

def superficie(row1, col1, row2, col2):
    return (abs(row1 - row2) + 1) * (abs(col1 - col2) + 1)

def list_other_neighbors(row, col, ingredient):
    neighbors = []

    for di in range(-max_cells + 1, max_cells):
        for dj in range(-max_cells + 1, max_cells):
            if di == 0 and dj == 0:
                continue

            i = row + di
            j = col + dj

            if i < 0 or i >= max_row or j < 0 or j >= max_col:
                continue

            if superficie(i, j, row, col) > max_cells or pizza[i][j] != ingredient or slices[i][j] != 0:
                continue

            neighbors.append((i, j))

    return neighbors

def count_ingredient(p1, p2, ingredient):
    count = 0
    for i in range(p1[0], p2[0] + 1):
        for j in range(p1[1], p2[1] + 1):
            count += int(pizza[i][j] == ingredient)

    return count

def make_slice(p1, p2, slice_number):
    for i in range(p1[0], p2[0] + 1):
        for j in range(p1[1], p2[1] + 1):
            slices[i][j] = slice_number

    popopo.append((p1, p2))
    # print('SLICE: {} {}'.format(p1, p2))

def is_free(p1, p2):
    for i in range(p1[0], p2[0] + 1):
        for j in range(p1[1], p2[1] + 1):
            if slices[i][j] != 0:
                return False
    return True

slice_number = 1
for row in range(len(pizza)):
    for col in range(len(pizza[row])):
        # If it's underrepresented and not attributed yet to a slice
        if pizza[row][col] == underrepresented and slices[row][col] == 0:
            others = list_other_neighbors(row, col, other(pizza[row][col]))
            sames = list_other_neighbors(row, col, pizza[row][col])

            if len(others) < min_ingredient:
                continue

            stack = []
            ok = False
            for oidx in range(0, len(others)):
                stack.append(others[oidx])

                for ooidx in range(oidx + 1, len(others)):
                    if len(stack) < min_ingredient:
                        stack.append(others[ooidx])
                    else:
                        corners = find_corners([(row, col)], stack)
                        if superficie(corners[0][0], corners[0][1], corners[1][0], corners[1][1]) > max_cells:
                            stack = stack[:-2]
                        elif count_ingredient(corners[0], corners[1], 'T') >= min_ingredient and count_ingredient(corners[0], corners[1], 'M') >= min_ingredient and is_free(corners[0], corners[1]):
                            make_slice(corners[0], corners[1], slice_number)
                            slice_number += 1
                            ok = True
                            break

                if ok: break

print(len(popopo))
for s in popopo:
    print('{} {} {} {}'.format(s[0][0], s[0][1], s[1][0], s[1][1]))
