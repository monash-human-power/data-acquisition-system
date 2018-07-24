#include <pigpio.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int pin = 4;
    int fs = 4000;
    int run_time = 20;	// length of run in seconds
    int screen = 0;
    int samples = fs*run_time;

    int i;
    int *p;
    double *t;

    p = malloc(samples*sizeof(int));
    t = malloc(samples*sizeof(double));

    gpioInitialise();
    gpioSetPullUpDown(pin,PI_PUD_UP);

    printf("\nStarting run....");

    double tstart=time_time();
    for(i = 0; i < samples; i++)
    {
	if(screen)
	{
	    printf("\n%d",gpioRead(pin));
	}
	else
	{
	    p[i] = gpioRead(pin);
	    t[i] = time_time() - tstart;
	}
	time_sleep(0.00025);
    }

    printf("\nWriting to file....\n\n");

    FILE *f;
    f = fopen("velocity.csv","w");
    for(i = 0; i < samples; i++)
    {
        fprintf(f,"\n%.5f, %d",t[i],p[i]);
    }
    fclose(f);
    return 0;
}
