import os
import cv2
import argparse
import numpy as np

# Map's scale
scale = 50



def read_room_colors_from_file(file_path):
    """Reads room colors from an extracted text file in BGR order for interpretation."""
    colors = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'color' in line:
                try:
                    color_info = line.split('color ')[1].strip()
                    color_parts = color_info.strip('[]').split(', ')
                    bgr = [int(part.split(': ')[1]) for part in color_parts]
                    colors.append(tuple(bgr))
                except (IndexError, ValueError) as e:
                    print(f"Error processing line: {line}")
                    print(e)
    return colors

def find_rooms_with_colors(image, target_colors):
    """Find rooms with specific colors."""
    found_colors = {}
    for color in target_colors:
        mask = cv2.inRange(image, np.array(color), np.array(color))
        if np.count_nonzero(mask) > 0:
            found_colors[tuple(color)] = {'mask': mask}
    return found_colors

def detect_adjacency(image, color_masks):
    """Detect adjacency between rooms based on color masks."""
    adjacency = {}
    for color, data in color_masks.items():
        mask = data['mask']
        room_number = data['room']
        adjacency[room_number] = set()
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=1)
        for other_color, other_data in color_masks.items():
            if color == other_color:
                continue
            other_mask = other_data['mask']
            overlap = cv2.bitwise_and(dilated_mask, other_mask)
            if np.any(overlap):
                adjacent_room = other_data['room']
                adjacency[room_number].add(adjacent_room)
    return adjacency

def calculate_distance(pt1, pt2):
    """Calculate the distance between two points."""
    return np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def process_floor_plan(image_path, center_rgb_file_path):

    image = cv2.imread(image_path)
    image_with_rectangles = image.copy()
    specified_colors_bgr = read_room_colors_from_file(center_rgb_file_path)
    
    add_output_text = '_interpreted'
    add_rectangle_text = '_interpreted_with_rectangles'
    base, ext = os.path.splitext(image_path)
    
    output_path = f"{base}{add_output_text}{ext}"
    rectangle_output_path = f"{base}{add_rectangle_text}{ext}"
    txt_output_path = base + '.txt'



    color_masks = {}
    room_id = 1
    for color in specified_colors_bgr:
        mask = cv2.inRange(image, color, color)
        mask = cv2.inRange(image_with_rectangles, color, color)
        area = np.count_nonzero(mask)
        if area == 0:
            continue
        
        room_number = f"Room {str(room_id).zfill(3)}"
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centroid_x, centroid_y = None, None
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                centroid_x = int(M["m10"] / M["m00"])
                centroid_y = int(M["m01"] / M["m00"])
                cv2.circle(image, (centroid_x, centroid_y), 5, (0, 255, 0), -1)
                cv2.putText(image, room_number, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.circle(image_with_rectangles, (centroid_x, centroid_y), 5, (0, 255, 0), -1)
                cv2.putText(image_with_rectangles, room_number, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Estimate approximated rectangle
            rect = cv2.minAreaRect(c)  
            box = cv2.boxPoints(rect)  
            box = np.intp(box)
            cv2.drawContours(image_with_rectangles, [box], 0, (0, 255, 0), 2)

            # Calculate lengths of the rectangle's sides
            length_a = round(calculate_distance(box[0], box[1])/scale, 2)
            length_b = round(calculate_distance(box[1], box[2])/scale, 2)

            if (length_a >= length_b):
                length = length_a
                width = length_b
            else:
                length = length_b
                width = length_a

            # Optionally, draw the room color and dimensions on the image for visualization
            #room_color = f"BGR{color}"
            #dimensions_text = f"L: {length:.2f}, W: {width:.2f}"
            #cx, cy = np.mean(box, axis=0)  # Calculate the center point of the box for text placement
            #cv2.putText(image, room_color, (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            #cv2.putText(image, dimensions_text, (int(cx), int(cy) + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        color_rgb = color[::-1]
        color_masks[tuple(color)] = {'mask': mask, 'room': room_number, 'color_rgb': tuple(color_rgb), 'area': area, 'centroid': (centroid_x, centroid_y), 'length': length, 'width': width}

        room_id += 1

    adjacency = detect_adjacency(image, color_masks)
    total_area = sum(data['area'] for room, data in color_masks.items())

    # Get Full image size
    full_image_a, full_image_b, _ = image.shape
    if (full_image_a >= full_image_b):
        full_length = round(full_image_a/scale, 2)
        full_width = round(full_image_b/scale, 2)
    else:
        full_length = round(full_image_b/scale, 2)
        full_width = round(full_image_a/scale, 2)

    with open(txt_output_path, 'w') as file:
        
        room_size_info = f"Entire Map's size is ({full_length}, {full_width})\n"
        file.write(room_size_info)

        for room, data in sorted(color_masks.items(), key=lambda x: x[1]['room']):
            neighbors = adjacency[data['room']]
            centroid = data['centroid']
            # print(f"{data['room']}: Color (RGB): {data['color_rgb']}, Area: {data['area']}/{total_area} pixels, Centroid: {centroid}, Length and Width: ({length}, {width}) Adjacent to: {', '.join(sorted(neighbors)) if neighbors else 'No adjacent rooms'}")
            # print(f"{data['room']} - Area: {data['area']}/{total_area} pixels, Length and Width: ({data['length']}, {data['width']}) Adjacent to: {', '.join(sorted(neighbors)) if neighbors else 'No adjacent rooms'}")
            area = round(data['area']/total_area*100, 2)
            each_room_info = f"{data['room']} - Area: {area} % in entire map, Approximate length and width: ({data['length']}, {data['width']}), Adjacent to: {', '.join(sorted(neighbors)) if neighbors else 'No adjacent rooms'}\n"
            file.write(each_room_info)

    cv2.imwrite(output_path, image)
    cv2.imwrite(rectangle_output_path, image_with_rectangles)



# Main

parser = argparse.ArgumentParser(description="Process some paths.")
parser.add_argument('--input1', type=str, required=False, default='--', help='The segmented_map_file path')
parser.add_argument('--input2', type=str, required=False, default='--', help='The bgr_center_input_file path')

args = parser.parse_args()

image_path = args.input1
center_rgb_file_path = args.input2

process_floor_plan(image_path, center_rgb_file_path)
