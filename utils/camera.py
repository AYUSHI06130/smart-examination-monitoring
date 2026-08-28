import cv2
import os
import time


def capture_photo(candidate_id, timeout_seconds=15):
    """
    Opens webcam and captures one photo.

    SPACE -> Capture photo
    ESC   -> Cancel
    """

    # ---------------------------------
    # Create uploads folder
    # ---------------------------------

    upload_folder = "static/uploads"

    os.makedirs(upload_folder, exist_ok=True)

    # ---------------------------------
    # Open Webcam
    # ---------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("Unable to access webcam.")

        return None

    print("\n====================================")
    print("Camera Started")
    print("Press SPACE to capture photo.")
    print("Press ESC to cancel.")
    print("====================================\n")

    photo_path = os.path.join(
        upload_folder,
        f"{candidate_id}.jpg"
    )

    start_time = time.monotonic()

    try:
        while time.monotonic() - start_time < timeout_seconds:

            success, frame = camera.read()

            if not success:

                print("Failed to read frame.")

                break

            cv2.imshow("Capture Candidate Photo", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 32:

                cv2.imwrite(photo_path, frame)

                print("Photo Saved Successfully.")

                break

            if key == 27:

                print("Photo Capture Cancelled.")

                photo_path = None

                break
        else:
            print("Photo capture timed out.")
            photo_path = None
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return photo_path