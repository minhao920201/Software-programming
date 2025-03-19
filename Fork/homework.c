#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int main()
{
	unsigned int status;
	int fd1, fd2, i;
	char input[100];
	scanf("%s", input);
	fd1 = open(input, O_RDONLY, S_IREAD);
	if (fd1 == -1)
	{
		printf("%s doesn't exist\n", input);
		return;
	}
	i = fork();
	if (i == 0)
	{
		fd2 = open("result", O_WRONLY | O_CREAT, S_IREAD | S_IWRITE);
		if (fd2 == -1)
		{
			printf("failed to create file\n");
			close(fd1);
			return;
		}
		close(0);
		dup(fd1);
		close(fd1);
		close(1);
		dup(fd2);
		close(fd2);
		execlp("wc", "wc", NULL);
	}
	else
	{
		close(fd1);
		wait(&status);
		fd1 = open("result", O_RDONLY, S_IREAD);
		if (fd1 == -1)
		{
			printf("result doesn't exist\n");
		}
		int num1, num2, num3;
		char buffer[80];
		int bytesRead = read(fd1, buffer, sizeof(buffer));
		buffer[bytesRead] = 0;
		sscanf(buffer, "%d %d %d", &num1, &num2, &num3);
		printf("Lines: %d, Words: %d\n", num1, num2);
		close(fd1);
	}
}
