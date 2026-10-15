#include "can.hpp"
#include "can.h"

Can::Can()
{

}

Can::~Can()
{

}

void Can::config()
{
    CAN_FilterTypeDef filter = {
        .FilterIdHigh = 0x0000,
        .FilterIdLow = 0x0000,
        .FilterMaskIdHigh = 0x0000,
        .FilterMaskIdLow = 0x0000,
        .FilterFIFOAssignment = CAN_RX_FIFO0,
        .FilterBank = 0,
        .FilterMode = CAN_FILTERMODE_IDMASK,
        .FilterScale = CAN_FILTERSCALE_32BIT,
        .FilterActivation = ENABLE,
        .SlaveStartFilterBank = 14,
    };

    HAL_CAN_ConfigFilter(&hcan, &filter);
}

void Can::start()
{
    HAL_CAN_Start(&hcan);
    uint32_t flags = CAN_IT_RX_FIFO0_MSG_PENDING | CAN_IT_TX_MAILBOX_EMPTY | CAN_IT_ERROR;
    HAL_CAN_ActivateNotification(&hcan, flags);
}

void Can::send(uint32_t id, uint8_t* data, uint32_t size)
{
    CAN_TxHeaderTypeDef header = {
        .StdId = id,
        .ExtId = 0,
        .IDE = CAN_ID_STD,
        .RTR = CAN_RTR_DATA,
        .DLC = size,
        .TransmitGlobalTime = DISABLE,
    };

    HAL_CAN_AddTxMessage(&hcan, &header, data, 0);
}

void Can::sendTpdo1(uint16_t nodeId, uint8_t *data, uint32_t size)
{
    send(nodeId + CobId::TPDO1, data, size);
}