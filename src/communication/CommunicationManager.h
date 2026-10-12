#pragma once

#include <cstdint>
#include <string>
#include <vector>

class CommunicationManager
{
public:
    CommunicationManager();
    ~CommunicationManager();

    bool init();

    bool sendMessage(const std::string& message);

    bool sendMessages(
        const std::vector<std::string>& messages
    );

    bool isConnected() const;

private:
    static constexpr std::uint16_t TELEMETRY_PORT = 9001;

    int serverSocket;
    int clientSocket;

    bool serverReady;
    bool connected;

    bool acceptClient();
    void disconnectClient();
};