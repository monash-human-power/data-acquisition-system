#pragma once

#include <mutex>
#include <array>

template <class T, size_t N>
class RingBuffer
{
    mutable std::mutex mutex_;
    std::array<T, N> buffer_;
    typename std::array<T, N>::iterator head_;
    bool full_ = false;

public:
    RingBuffer();

    void put(const T item);
    bool contains(const T item) const;
};

template <class T, size_t N>
RingBuffer<T, N>::RingBuffer()
{
    this->head_ = this->buffer_.begin();
}

template <class T, size_t N>
void RingBuffer<T, N>::put(T item)
{
    std::lock_guard<std::mutex> lock(this->mutex_);

    *this->head_++ = item;
    if (this->head_ == this->buffer_.end())
    {
        this->head_ = this->buffer_.begin();
        this->full_ = true;
    }
}

template <class T, size_t N>
bool RingBuffer<T, N>::contains(T item) const
{
    std::lock_guard<std::mutex> lock(this->mutex_);

    // Only iterate until the head if the array is not yet full
    auto stop = this->full_ ? this->buffer_.end() : this->head_;

    for (auto it = this->buffer_.begin(); it < stop; it++)
        if (*it == item)
            return true;
    return false;
}