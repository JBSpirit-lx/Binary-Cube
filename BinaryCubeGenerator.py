import math
from tqdm import tqdm

# https://medium.vaningelgem.be/python-rounding-as-taught-in-school-29fb77966cf0
def school_round(num, ndigits=0):
    digits = str(num).split('.')
    if len(digits) == 1:  # int
        exponent = 0
    elif len(digits) == 2:  # float
        exponent = len(digits[1])
    else:
        raise ValueError(f"Cannot interpret '{num}' as a number.")
    tmp = num
    for exp in range(exponent - 1, ndigits - 1, -1):
        exp = 10**exp
        tmp = int(tmp * exp + 0.5) / exp
    if ndigits <= 0:
        return int(tmp)
    return tmp


def str_tuple(tup):
    tup_str = ""
    for i in tup:
        tup_str += str(i) + " "
    return tup_str.strip()


def calculate_normal(p1, p2, p3):
    vector_ab = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    vector_ac = [p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]]
    i = (vector_ab[1] * vector_ac[2]) - (vector_ac[1] * vector_ab[2])
    j = (vector_ab[0] * vector_ac[2]) - (vector_ac[0] * vector_ab[2])
    k = (vector_ac[0] * vector_ab[1]) - (vector_ab[0] * vector_ac[1])
    normal_vector = [i, j, k]
    vector_magnitude = math.sqrt(math.pow(i, 2) + math.pow(j, 2) + math.pow(k, 2))
    unit_vector = []
    for scalar in normal_vector:
        unit_vector.append(str(school_round((scalar / vector_magnitude), 5)))
    return ' '.join(unit_vector)


def create_triangle_content(point1, point2, point3):
    sub_content = "facet normal " + calculate_normal(point1, point2, point3) + "\n"
    sub_content += "outer loop\n"
    sub_content += "vertex " + str_tuple(point1) + "\n"
    sub_content += "vertex " + str_tuple(point2) + "\n"
    sub_content += "vertex " + str_tuple(point3) + "\n"
    sub_content += "endloop\n"
    sub_content += "endfacet\n"
    return sub_content


def create_square(v1, v2, v3, v4):
    triangle1 = create_triangle_content(v1, v2, v3)
    triangle2 = create_triangle_content(v1, v3, v4)
    return triangle1 + triangle2


def simplify_mesh(complex_mesh):
    pass


# input and process data
binaryDataList = []
with open("imgx16.png", "rb") as file:
    fileContent = file.read()
    for byte in tqdm(fileContent,
        desc="Processing File",
        total=len(fileContent),
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"):

        binary_string = format(byte, '08b')
        binaryDataList.extend(list(binary_string))

total_bits = len(binaryDataList)
sideWidth = math.ceil(math.sqrt(total_bits / 4))

# Binary Vertex Distribution - used to associate each bit with its respective vertex
bvd = [[[]]] # When accessing: bvd[face][current_z][current_x/current_y]
current_x = 0
current_y = 0
current_z = 0
current_face = 0
for bit in tqdm(binaryDataList,
                desc="Mapping Binary",
                total=total_bits,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"):
    if current_face == 0:
        bvd[current_face][current_z].append(bit)
        current_x += 1
        if current_x == sideWidth:
            current_x = 0
            current_z += 1
            if current_z == sideWidth:
                current_z = 0
                bvd.append([[]])
                current_face += 1
            else:
                bvd[current_face].append([])
    if current_face == 1:
        bvd[current_face][current_z].append(bit)
        current_y += 1
        if current_y == sideWidth:
            current_y = 0
            current_z += 1
            if current_z == sideWidth:
                current_z = 0
                bvd.append([[]])
                current_face += 1
                current_x = sideWidth
            else:
                bvd[current_face].append([])
    if current_face == 2:
        bvd[current_face][current_z].append(bit)
        current_x -= 1
        if current_x == 0:
            current_x = sideWidth
            current_z += 1
            if current_z == sideWidth:
                current_z = 0
                bvd.append([[]])
                current_face += 1
                current_y = sideWidth
            else:
                bvd[current_face].append([])
    if current_face == 3:
        bvd[current_face][current_z].append(bit)
        current_y -= 1
        if current_y == 0:
            current_y = sideWidth
            current_z += 1
            if current_z == sideWidth:
                current_z = 0
            else:
                bvd[current_face].append([])
while current_y > 0:
    bvd[current_face][current_z].append('0')
    current_y -= 1
while current_z < sideWidth:
    bvd[current_face].append(['0'] * sideWidth)
    current_z += 1

# create file content
subContent = ""
current_x = 0
current_y = 0
current_z = 0
relBinary_x = 0
relBinary_y = 0
current_face = 0
relevantVertices = []
MIN_ITERATIONS_BETWEEN_UPDATES = total_bits / 200
file_name = "new_obj.stl"
with open(file_name, "w") as file:

    file.write("solid new_obj\n")

    for bit in tqdm(binaryDataList,
                    desc="Generating Object",
                    total=total_bits,
                    miniters=MIN_ITERATIONS_BETWEEN_UPDATES,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"):
        if current_face == 0:
            relevantVertices = [(current_x, 0, current_z),
                                (current_x + 1, 0, current_z),
                                (current_x + 1, 0, current_z + 1),
                                (current_x, 0, current_z + 1)]
            if bit == "1":
                relevantVertices += [(current_x, -1, current_z),
                                     (current_x + 1, -1, current_z),
                                     (current_x + 1, -1, current_z + 1),
                                     (current_x, -1, current_z + 1)]
                # front-face
                file.write(create_square(relevantVertices[4], relevantVertices[5], relevantVertices[6], relevantVertices[7]))
                if current_x == 0 or bvd[current_face][current_z][current_x - 1] == "0": # if the previous bit is 0
                    # right-side-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[7], relevantVertices[3]))
                if current_x == (sideWidth - 1) or bvd[current_face][current_z][current_x + 1] == "0":  # if the next bit is 0
                    # left-side-face
                    file.write(create_square(relevantVertices[1], relevantVertices[5], relevantVertices[6], relevantVertices[2]))
                if current_z == (sideWidth - 1) or bvd[current_face][current_z + 1][current_x] == "0": # if the bit above is 0
                    # top-face
                    file.write(create_square(relevantVertices[3], relevantVertices[7], relevantVertices[6], relevantVertices[2]))
                if current_z == 0 or bvd[current_face][current_z - 1][current_x] == "0": # if the bit below is 0
                    # bottom-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[5], relevantVertices[1]))
            else:
                file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))
            current_x += 1
            if current_x == sideWidth:
                current_x = 0
                current_z += 1
                if current_z == sideWidth:
                    current_z = 0
                    current_face += 1
        if current_face == 1:
            relevantVertices = [(sideWidth, current_y, current_z),
                                (sideWidth, current_y + 1, current_z),
                                (sideWidth, current_y + 1, current_z + 1),
                                (sideWidth, current_y, current_z + 1)]
            if bit == "1":
                relevantVertices += [(sideWidth + 1, current_y, current_z),
                                    (sideWidth + 1, current_y + 1, current_z),
                                    (sideWidth + 1, current_y + 1, current_z + 1),
                                    (sideWidth + 1, current_y, current_z + 1)]
                # front-face
                file.write(create_square(relevantVertices[4], relevantVertices[5], relevantVertices[6], relevantVertices[7]))
                if current_y == 0 or bvd[current_face][current_z][current_y - 1] == "0": # if the previous bit is 0
                    # right-side-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[7], relevantVertices[3]))
                if current_y == (sideWidth - 1) or bvd[current_face][current_z][current_y + 1] == "0":  # if the next bit is 0
                    # left-side-face
                    file.write(create_square(relevantVertices[1], relevantVertices[5], relevantVertices[6], relevantVertices[2]))
                if current_z == (sideWidth - 1) or bvd[current_face][current_z + 1][current_y] == "0": # if the bit above is 0
                    # top-face
                    file.write(create_square(relevantVertices[3], relevantVertices[7], relevantVertices[6], relevantVertices[2]))
                if current_z == 0 or bvd[current_face][current_z - 1][current_y] == "0": # if the bit below is 0
                    # bottom-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[5], relevantVertices[1]))
            else:
                file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))
            current_y += 1
            if current_y == sideWidth:
                current_y = 0
                current_z += 1
                if current_z == sideWidth:
                    current_z = 0
                    current_face += 1
                    current_x = sideWidth
        if current_face == 2:
            relevantVertices = [(current_x, sideWidth, current_z),
                                (current_x - 1, sideWidth, current_z),
                                (current_x - 1, sideWidth, current_z + 1),
                                (current_x, sideWidth, current_z + 1)]
            if bit == "1":
                relevantVertices += [(current_x, sideWidth + 1, current_z),
                                     (current_x - 1, sideWidth + 1, current_z),
                                     (current_x - 1, sideWidth + 1, current_z + 1),
                                     (current_x, sideWidth + 1, current_z + 1)]
                # front-face
                file.write(create_square(relevantVertices[4], relevantVertices[5], relevantVertices[6], relevantVertices[7]))
                if current_x == sideWidth or bvd[current_face][current_z][relBinary_x - 1] == "0": # if the previous bit is 0
                    # right-side-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[7], relevantVertices[3]))
                if current_x == 1 or bvd[current_face][current_z][relBinary_x + 1] == "0":  # if the next bit is 0
                    # left-side-face
                    file.write(create_square(relevantVertices[1], relevantVertices[5], relevantVertices[6], relevantVertices[2]))
                if current_z == (sideWidth - 1) or bvd[current_face][current_z + 1][relBinary_x] == "0": # if the bit above is 0
                    # top-face
                    file.write(create_square(relevantVertices[3], relevantVertices[7], relevantVertices[6], relevantVertices[2]))
                if current_z == 0 or bvd[current_face][current_z - 1][relBinary_x] == "0": # if the bit below is 0
                    # bottom-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[5], relevantVertices[1]))
            else:
                file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))
            current_x -= 1
            relBinary_x += 1
            if current_x == 0:
                current_x = sideWidth
                relBinary_x = 0
                current_z += 1
                if current_z == sideWidth:
                    current_z = 0
                    current_face += 1
                    current_y = sideWidth
        if current_face == 3:
            relevantVertices = [(0, current_y, current_z),
                                (0, current_y - 1, current_z),
                                (0, current_y - 1, current_z + 1),
                                (0, current_y, current_z + 1)]
            if bit == "1":
                relevantVertices += [(-1, current_y, current_z),
                                    (-1, current_y - 1, current_z),
                                    (-1, current_y - 1, current_z + 1),
                                    (-1, current_y, current_z + 1)]
                # front-face
                file.write(create_square(relevantVertices[4], relevantVertices[5], relevantVertices[6], relevantVertices[7]))
                if current_y == sideWidth or bvd[current_face][current_z][relBinary_y - 1] == "0": # if the previous bit is 0
                    # right-side-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[7], relevantVertices[3]))
                if current_y == 1 or bvd[current_face][current_z][relBinary_y + 1] == "0":  # if the next bit is 0
                    # left-side-face
                    file.write(create_square(relevantVertices[1], relevantVertices[5], relevantVertices[6], relevantVertices[2]))
                if current_z == (sideWidth - 1) or bvd[current_face][current_z + 1][relBinary_y] == "0": # if the bit above is 0
                    # top-face
                    file.write(create_square(relevantVertices[3], relevantVertices[7], relevantVertices[6], relevantVertices[2]))
                if current_z == 0 or bvd[current_face][current_z - 1][relBinary_y] == "0": # if the bit below is 0
                    # bottom-face
                    file.write(create_square(relevantVertices[0], relevantVertices[4], relevantVertices[5], relevantVertices[1]))
            else:
                file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))
            current_y -= 1
            relBinary_y += 1
            if current_y == 0:
                current_y = sideWidth
                relBinary_y = 0
                current_z += 1
                # if current_z == sideWidth:
                #     current_z = 0
                #     current_face += 1
                #     current_x = sideWidth

    print("Cleaning up...")

    # fill out the rest of the last side with 0's (just 1-2 big flat face(s) for optimization)
    if current_y > 0:
        relevantVertices = [(0, current_y, current_z),
                            (0, 0, current_z),
                            (0, 0, current_z + 1),
                            (0, current_y, current_z + 1)]
        file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))
    if current_z + 1 < sideWidth:
        relevantVertices = [(0, sideWidth, current_z + 1),
                            (0, 0, current_z + 1),
                            (0, 0, sideWidth),
                            (0, sideWidth, sideWidth)]
        file.write(create_square(relevantVertices[0], relevantVertices[1], relevantVertices[2], relevantVertices[3]))

    # these lines that are commented out can be used to generate the cube hollow...
    # generate bottom and top faces
    # file.write(create_square((0, 0, 0), (1, 0, 0), (1, sideWidth, 0), (0, sideWidth, 0)))
    # file.write(create_square((sideWidth - 1, 0, 0), (sideWidth, 0, 0), (sideWidth, sideWidth, 0), (sideWidth - 1, sideWidth, 0)))
    # file.write(create_square((1, 0, 0), (sideWidth - 1, 0, 0), (sideWidth - 1, 1, 0), (1, 1, 0)))
    # file.write(create_square((1, sideWidth - 1, 0), (sideWidth - 1, sideWidth - 1, 0), (sideWidth - 1, sideWidth, 0), (1, sideWidth, 0)))
    #
    # file.write(create_square((0, 0, sideWidth), (1, 0, sideWidth), (1, sideWidth, sideWidth), (0, sideWidth, sideWidth)))
    # file.write(create_square((sideWidth - 1, 0, sideWidth), (sideWidth, 0, sideWidth), (sideWidth, sideWidth, sideWidth), (sideWidth - 1, sideWidth, sideWidth)))
    # file.write(create_square((1, 0, sideWidth), (sideWidth - 1, 0, sideWidth), (sideWidth - 1, 1, sideWidth), (1, 1, sideWidth)))
    # file.write(create_square((1, sideWidth - 1, sideWidth), (sideWidth - 1, sideWidth - 1, sideWidth), (sideWidth - 1, sideWidth, sideWidth), (1, sideWidth, sideWidth)))
    #
    # # generate interior sides
    # file.write(create_square((1, 1, 0), (sideWidth - 1, 1, 0), (sideWidth - 1, 1, sideWidth), (1, 1, sideWidth)))
    # file.write(create_square((1, sideWidth - 1, 0), (sideWidth - 1, sideWidth - 1, 0), (sideWidth - 1, sideWidth - 1, sideWidth), (1, sideWidth - 1, sideWidth)))
    # file.write(create_square((1, 1, 0), (1, sideWidth - 1, 0), (1, sideWidth - 1, sideWidth), (1, 1, sideWidth)))
    # file.write(create_square((sideWidth - 1, 1, 0), (sideWidth - 1, sideWidth - 1, 0), (sideWidth - 1, sideWidth - 1, sideWidth), (sideWidth - 1, 1, sideWidth)))

    # generate top and bottom lid
    file.write(create_square((0, 0, 0), (sideWidth, 0, 0), (sideWidth, sideWidth, 0), (0, sideWidth, 0)))
    file.write(create_square((0, 0, sideWidth), (sideWidth, 0, sideWidth), (sideWidth, sideWidth, sideWidth), (0, sideWidth, sideWidth)))

    file.write("endsolid new_obj")

# simplify the mesh
# (yet to be programmed)

print("Object file created as 'new_obj.stl'")
print(f"Object dimensions: {sideWidth / 10}cm^3")

