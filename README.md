How to compile compile code:
cd ~/data-acquisition-system

g++ -std=c++17 $(find src -name "*.cpp") \
-I. \
-Isrc \
-Isrc/sensors \
-Isrc/data \
-Isrc/config \
-Isrc/core \
-Isrc/hardware \
-Isrc/communication \
-o vcu