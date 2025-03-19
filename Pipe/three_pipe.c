#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#define ERR (-1)
#define READ 0
#define WRITE 1
#define STDIN 0
#define STDOUT 1

int main()
{
	int pid1, pid2, pid3, pid4, pfd1[2], pfd2[2], pfd3[2];

	if (pipe(pfd1) == ERR)
	{
		perror("pipe1");
		exit(ERR);
	}

	if ( (pid1 = fork()) == ERR )
	{
		perror("fork1");
		exit(ERR);
	}

	if (pid1 == 0)
	{
		close(STDOUT);
		dup(pfd1[WRITE]);
		close(pfd1[READ]);
		close(pfd1[WRITE]);
		execlp("ps", "ps", "aux", NULL);
	}
	

	if (pipe(pfd2) == ERR)
	{
		perror("pipe2");
		exit(ERR);
	}
	
	if ( (pid2 = fork()) == ERR )
	{
		perror("fork2");
		exit(ERR);
	}

	if (pid2 == 0)
	{
		close(STDIN);
		dup(pfd1[READ]);
		close(STDOUT);
		dup(pfd2[WRITE]);
		close(pfd1[READ]);
		close(pfd1[WRITE]);
		close(pfd2[READ]);
		close(pfd2[WRITE]);
		execlp("grep", "grep", "41071102H", NULL);
	}
	
	
	close(pfd1[READ]);
	close(pfd1[WRITE]);

	if (pipe(pfd3) == ERR)
	{
		perror("pipe3");
		exit(ERR);
	}
	if ( (pid3 = fork()) == ERR )
	{
		perror("fork3");
		exit(ERR);
	}

	if (pid3 == 0)
	{
		close(STDIN);
		dup(pfd2[READ]);
		close(STDOUT);
		dup(pfd3[WRITE]);
		close(pfd2[READ]);
		close(pfd2[WRITE]);
		close(pfd3[READ]);
		close(pfd3[WRITE]);
		execlp("grep", "grep", "-v", "grep", NULL);
	}
	
	close(pfd2[READ]);
	close(pfd2[WRITE]);
	
	if ( (pid4 = fork()) == ERR )
	{
		perror("fork4");
		exit(ERR);
	}

	if (pid4 == 0)
	{
		close(STDIN);
		dup(pfd3[READ]);

		int fd = open("the_result", O_WRONLY | O_CREAT | O_TRUNC, S_IREAD | S_IWRITE);
		if (fd == ERR)
		{
			perror("open");
			exit(ERR);
		}
		close(STDOUT);
		dup(fd);
		close(fd);


		close(pfd3[READ]);
		close(pfd3[WRITE]);
		execlp("wc", "wc", NULL);
	}

	close(pfd3[READ]);
	close(pfd3[WRITE]);
	wait((int *) 0);
	wait((int *) 0);
	wait((int *) 0);
	wait((int *) 0);
	exit(0);
}
