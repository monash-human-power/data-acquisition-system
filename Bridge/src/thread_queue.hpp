#pragma once

#include <mutex>
#include <optional>
#include <queue>

/**
 * A simple wrapper of std::queue which is thread-safe.
 */
template<class T>
class ThreadQueue
{
    std::mutex mutex_;
    std::queue<T> queue_;

public:
    /**
     * Pushes an item to the back of the queue.
     * @param item the item to be added to the queue.
     */
    void push(const T item);
    /**
     * Pops an item from the front of the queue, removing it.
     * @return the popped item if one exists, otherwise std::nullopt.
     */
    std::optional<T> pop();
};

template<class T>
void ThreadQueue<T>::push(const T item)
{
    std::lock_guard<std::mutex> lock(this->mutex_);
    this->queue_.push(item);
}

template<class T>
std::optional<T> ThreadQueue<T>::pop()
{
    std::lock_guard<std::mutex> lock(this->mutex_);
    if (this->queue_.empty())
        return { };
    auto item = this->queue_.front();
    this->queue_.pop();
    return item;
}
