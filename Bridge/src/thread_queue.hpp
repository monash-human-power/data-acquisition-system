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
     * @param item The item to be added to the queue.
     */
    void push(const T item);
    /**
     * Pushes a vector of items into the queue.
     * The first item in the vector will be added to the queue first.
     * @param items The vector of items to be pushed.
     */
    void push(const std::vector<T> item);
    /**
     * Pops an item from the front of the queue, removing it.
     * @return The popped item if one exists, otherwise std::nullopt.
     */
    std::optional<T> pop();
    /**
     * Returns the size of the queue
    */
    size_t size();
};

template<class T>
void ThreadQueue<T>::push(const T item)
{
    std::lock_guard<std::mutex> lock(this->mutex_);
    this->queue_.push(item);
}

template<class T>
void ThreadQueue<T>::push(const std::vector<T> items)
{
    std::lock_guard<std::mutex> lock(this->mutex_);
    for (auto &&item : items)
        this->queue_.push(item);
}


template<class T>
size_t ThreadQueue<T>::size()
{
    std::lock_guard<std::mutex> lock(this->mutex_);
    return this->queue_.size();
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
