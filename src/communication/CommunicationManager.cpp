#include "CommunicationManager.h"

#include <iostream>

CommunicationManager::CommunicationManager()
    : connected(false)
{
}

bool CommunicationManager::init()
{
    std::cout << "Initialising communication manager..." << std::endl;

    // For now, we are pretending communication is ready.
    // Later, this is where BLE/Bluetooth setup would go.
    connected = true;

    std::cout << "Communication manager ready." << std::endl;

    return connected;
}

bool CommunicationManager::sendMessage(const std::string& message)
{
    if (!connected)
    {
        std::cerr << "Cannot send message: communication not connected."
                  << std::endl;

        return false;
    }

    // For now, just print the message.
    // Later, replace this with BLE send logic.
    std::cout << message << std::endl;

    return true;
}

bool CommunicationManager::sendMessages(const std::vector<std::string>& messages)
{
    bool allSuccessful = true;

    for (const std::string& message : messages)
    {
        bool success = sendMessage(message);

        if (!success)
        {
            allSuccessful = false;
        }
    }

    return allSuccessful;
}

bool CommunicationManager::isConnected() const
{
    return connected;
}