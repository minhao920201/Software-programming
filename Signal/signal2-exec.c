/*  timesup.c  */

     #include <stdio.h>
     #include <sys/signal.h>

     #define  EVER  ;;

     void main();
     int times_up();
     int controlc_up();

     void main()
     {
        signal (SIGALRM, times_up);         /* go to the times_up function  */
        signal (SIGINT, controlc_up);         /* go to the times_up function  */
                                            /* when the alarm goes off.     */
        alarm (10);                         /* set the alarm for 10 seconds */

        for (EVER)                          /* endless loop.                */
           ;                                /* hope the alarm works.        */
     }

     int times_up(sig)
     int sig;                               /* value of signal              */
     {
        printf("Caught signal #< %d >\n", sig);
        printf("Time's up!  I'm outta here!!\n");
	alarm(10);
        /* exit(sig);  */                        /* return the signal number     */
     }

     int controlc_up(sig)
     int sig;                               /* value of signal              */
     {
        int i = fork();
	if (i == 0)
	{
		execlp("uptime", "uptime", NULL);
	}
	i = fork();
	if (i == 0)
	{
		execlp("who", "who", NULL);
	}
       /* exit(sig);  */                        /* return the signal number     */
     }
