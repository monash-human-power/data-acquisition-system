#include "DataSerialiser.h"

#include <sstream>

std::string DataSerialiser::toJSON(
    const SensorReading& reading)
{
    std::stringstream ss;

    ss << "{";

    ss << "\"sensor\":\""
       << escapeJSONString(reading.sensorID)
       << "\",";

    ss << "\"timestamp\":"
       << reading.timestamp
       << ",";

    ss << "\"values\":{";

    bool firstValue = true;

    for (const auto& value : reading.values)
    {
        if (!firstValue)
        {
            ss << ",";
        }

        ss << "\""
           << escapeJSONString(value.first)
           << "\":"
           << value.second;

        firstValue = false;
    }

    ss << "},";

    ss << "\"valid\":"
       << (reading.isValid ? "true" : "false");

    ss << "}";

    return ss.str();
}

std::vector<std::string> DataSerialiser::toJSON(
    const std::vector<SensorReading>& readings)
{
    std::vector<std::string> output;

    output.reserve(readings.size());

    for (const SensorReading& reading : readings)
    {
        output.push_back(
            toJSON(reading)
        );
    }

    return output;
}

std::string DataSerialiser::escapeJSONString(
    const std::string& input)
{
    std::string output;

    for (char c : input)
    {
        switch (c)
        {
            case '"':
                output += "\\\"";
                break;

            case '\\':
                output += "\\\\";
                break;

            case '\n':
                output += "\\n";
                break;

            case '\r':
                output += "\\r";
                break;

            case '\t':
                output += "\\t";
                break;

            default:
                output += c;
                break;
        }
    }

    return output;
}