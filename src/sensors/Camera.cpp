#include "Camera.h"

#include <cstdlib>
#include <string>
#include <thread>
#include <chrono>

Camera::Camera(uint8_t deviceIndex)
    : cameraIndex(deviceIndex)
{
}

bool Camera::startStream()
{
    int mediaResult = std::system(
        "/home/mani2406/mediamtx "
        "/home/mani2406/mediamtx.yml "
        "> /tmp/mediamtx.log 2>&1 &"
    );

    if (mediaResult != 0)
    {
        return false;
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::string command =
        "rpicam-vid "
        "--camera " + std::to_string(cameraIndex) + " "
        "-t 0 "
        "--width 640 "
        "--height 360 "
        "--framerate 15 "
        "--codec libav "
        "--libav-format h264 "
        "--low-latency "
        "--inline "
        "-n "
        "-o - | "
        "ffmpeg "
        "-f h264 "
        "-framerate 15 "
        "-i - "
        "-c:v copy "
        "-f rtp "
        "\"udp://127.0.0.1:5004?pkt_size=1200\" "
        "> /tmp/camera.log 2>&1 &";

    int cameraResult = std::system(command.c_str());

    return cameraResult == 0;
}

void Camera::stopStream()
{
    std::system("pkill -f rpicam-vid");
    std::system("pkill -f ffmpeg");
    std::system("pkill -f /home/mani2406/mediamtx");
}