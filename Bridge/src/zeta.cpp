#include "zeta.hpp"

ZetaRfRadio::ZetaRfRadio()
{
    std::cout << "Starting Zeta TxRx..." << std::endl;

    if (!this->zeta_.beginWithPacketLengthOf(PACKET_LENGTH))
        throw "ZetaRf begin failed. Check wiring?";

    if (!this->zeta_.startListeningSinglePacketOnChannel(ZetaRfRadio::ZETA_CHANNEL))
        throw "ZetaRf startListening failed.";

    std::cout << "Init done." << std::endl;
}
