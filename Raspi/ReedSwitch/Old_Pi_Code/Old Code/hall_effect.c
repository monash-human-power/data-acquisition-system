#include <pigpio.h>
#include <stdio.h>

double start;

void aFunction(int gpio, int level, uint32_t tick)
{
   printf("\nGPIO %d became %d at %.2f\n", gpio, level, time_time()-start);
}

int main()
{
    start = time_time();

    if (gpioInitialise() < 0)
    {
        printf("Failed to initialize GPIO!");
        return 1;
    }

    while(1)
    {
        // call aFunction whenever GPIO 4 changes state
        gpioSetAlertFunc(4, aFunction);
	    time_sleep(0.1);
    }
    gpioTerminate();
    return 1;
}
