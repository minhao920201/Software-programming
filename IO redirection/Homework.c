#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int main()
{
	int fd1, fd2;
	fd1 = open("foo.bar", O_RDONLY, S_IREAD);
	close(0);
	dup(fd1);
	close(fd1);

	fd2 = open("result", O_WRONLY | O_CREAT, S_IREAD | S_IWRITE);

	close(1);
	dup(fd2);
	close(fd2);

	execlp("wc", "wc", NULL);
}