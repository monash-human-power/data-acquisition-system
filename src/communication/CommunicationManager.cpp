#include "CommunicationManager.h"

#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

CommunicationManager::CommunicationManager()
    : serverSocket(-1),
      clientSocket(-1),
      serverReady(false),
      connected(false)
{
}

CommunicationManager::~CommunicationManager()
{
    disconnectClient();

    if (serverSocket >= 0)
    {
        close(serverSocket);
        serverSocket = -1;
    }
}

bool CommunicationManager::init()
{
    std::cout
        << "Initialising communication manager..."
        << std::endl;

    serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (serverSocket < 0)
    {
        std::cerr
            << "Failed to create telemetry socket: "
            << std::strerror(errno)
            << std::endl;

        return false;
    }

    int reuseAddress = 1;

    if (setsockopt(
            serverSocket,
            SOL_SOCKET,
            SO_REUSEADDR,
            &reuseAddress,
            sizeof(reuseAddress)
        ) < 0)
    {
        std::cerr
            << "Warning: failed to enable SO_REUSEADDR."
            << std::endl;
    }

    sockaddr_in serverAddress{};

    serverAddress.sin_family = AF_INET;

    // Listen on every Pi network interface.
    // The phone will connect through 10.55.0.1.
    serverAddress.sin_addr.s_addr =
        htonl(INADDR_ANY);

    serverAddress.sin_port =
        htons(TELEMETRY_PORT);

    if (bind(
            serverSocket,
            reinterpret_cast<sockaddr*>(
                &serverAddress
            ),
            sizeof(serverAddress)
        ) < 0)
    {
        std::cerr
            << "Failed to bind telemetry socket: "
            << std::strerror(errno)
            << std::endl;

        close(serverSocket);
        serverSocket = -1;

        return false;
    }

    if (listen(serverSocket, 1) < 0)
    {
        std::cerr
            << "Failed to listen for telemetry client: "
            << std::strerror(errno)
            << std::endl;

        close(serverSocket);
        serverSocket = -1;

        return false;
    }

    // Make accept() non-blocking.
    // This means the VCU can continue reading sensors
    // even when the phone is not connected.
    int flags =
        fcntl(
            serverSocket,
            F_GETFL,
            0
        );

    if (flags >= 0)
    {
        fcntl(
            serverSocket,
            F_SETFL,
            flags | O_NONBLOCK
        );
    }

    serverReady = true;

    std::cout
        << "Telemetry server ready on port "
        << TELEMETRY_PORT
        << std::endl;

    std::cout
        << "Phone should connect to "
        << "10.55.0.1:"
        << TELEMETRY_PORT
        << std::endl;

    return true;
}

bool CommunicationManager::acceptClient()
{
    if (!serverReady)
    {
        return false;
    }

    if (clientSocket >= 0)
    {
        return true;
    }

    sockaddr_in clientAddress{};
    socklen_t clientLength =
        sizeof(clientAddress);

    int socket =
        accept(
            serverSocket,
            reinterpret_cast<sockaddr*>(
                &clientAddress
            ),
            &clientLength
        );

    if (socket < 0)
    {
        // No connection waiting.
        if (
            errno == EAGAIN ||
            errno == EWOULDBLOCK
        )
        {
            return false;
        }

        std::cerr
            << "Failed to accept telemetry client: "
            << std::strerror(errno)
            << std::endl;

        return false;
    }

    clientSocket = socket;
    connected = true;

    char clientIP[INET_ADDRSTRLEN]{};

    inet_ntop(
        AF_INET,
        &clientAddress.sin_addr,
        clientIP,
        sizeof(clientIP)
    );

    std::cout
        << "Telemetry client connected: "
        << clientIP
        << std::endl;

    return true;
}

bool CommunicationManager::sendMessage(
    const std::string& message)
{
    if (!serverReady)
    {
        return false;
    }

    if (!connected)
    {
        if (!acceptClient())
        {
            // Phone has not connected yet.
            // Keep the VCU running normally.
            return false;
        }
    }

    // Newline-delimited JSON.
    // Each line received by the phone is one complete JSON packet.
    std::string packet =
        message + "\n";

    std::size_t totalSent = 0;

    while (totalSent < packet.size())
    {
        ssize_t sent =
            send(
                clientSocket,
                packet.data() + totalSent,
                packet.size() - totalSent,
                MSG_NOSIGNAL
            );

        if (sent <= 0)
        {
            std::cerr
                << "Telemetry client disconnected."
                << std::endl;

            disconnectClient();

            return false;
        }

        totalSent +=
            static_cast<std::size_t>(sent);
    }

    return true;
}

bool CommunicationManager::sendMessages(
    const std::vector<std::string>& messages)
{
    bool allSuccessful = true;

    for (const std::string& message : messages)
    {
        if (!sendMessage(message))
        {
            allSuccessful = false;

            // If there is no phone connected yet,
            // there is no point trying the remaining
            // packets during this loop iteration.
            if (!connected)
            {
                break;
            }
        }
    }

    return allSuccessful;
}

bool CommunicationManager::isConnected() const
{
    return connected;
}

void CommunicationManager::disconnectClient()
{
    if (clientSocket >= 0)
    {
        close(clientSocket);
        clientSocket = -1;
    }

    connected = false;
}