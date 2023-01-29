#pragma once

#include <mutex>
#include <array>

/**
 * A very basic, thread safe implementation of a ring buffer.
 * Supports only adding items and checking if the item is contained. Items
 * cannot be explicitly removed, only overwritten.
 * @tparam T The type to be stored in the ring buffer.
 * @tparam N The size of the ring buffer, i.e. the maximum number of items to
 *           be stored.
 */
template <class T, size_t N>
class RingBuffer
{
    /**
     * The mutex used to ensure multiple threads cannot simultaneously access
     * the ring buffer.
     */
    mutable std::mutex mutex_;
    /**
     * Array in which added elements are stored. */
    std::array<T, N> buffer_;
    /** Iterator pointing to the next element to be written to. */
    typename std::array<T, N>::iterator head_;
    /** True if the internal array is at capacity. */
    bool full_ = false;

public:
    /** Create a new ring buffer. */
    RingBuffer();

    /**
     * Insert an item into the ring buffer.
     * @param item The item to be added.
     */
    void put(const T item);
    /**
     * Check if an item is contained within the ring buffer.
     * @param item The item to be queried.
     * @return True if the item is contained, else false.
     */
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