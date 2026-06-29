#pragma once

#include <string>
#include <vector>

class CommunicationManager
{
public:
    CommunicationManager();

    bool init();

    bool sendMessage(const std::string& message);

    bool sendMessages(const std::vector<std::string>& messages);

    bool isConnected() const;

private:
    bool connected;
};