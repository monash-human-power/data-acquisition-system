/**
 * Calculate a rolling average on a set of data points
 */
class RollingAverage {
  /**
   * Create a rolling average counter
   *
   * @param {number} interval Length of rolling interval window in milliseconds
   */
  constructor(interval) {
    this.interval = interval;
    this.points = [];
  }

  /**
   * Add data point to average
   *
   * @param {number} value Value
   */
  add(value) {
    const time = Date.now();
    this.points.push([time, value]);
  }

  /**
   * Calculate the current average value over the rolling interval
   *
   * @returns {number} Average value
   */
  average() {
    // Remove all stale values
    const time = Date.now();
    this.points = this.points.filter((x) => x[0] >= time - this.interval);

    const sum = this.points.reduce((acc, curr) => acc + curr[1], 0);
    const average = sum / this.points.length;
    return average;
  }
}

module.exports = RollingAverage;
