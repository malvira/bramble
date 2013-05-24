#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define SLEEP_TIME (50 * 1000) /* usec per held click */
#define LONG_HOLD_TIME (3000000) /* in usec */

#define THRESH (LONG_HOLD_TIME / SLEEP_TIME)
 
#define GPIO     "459" 
#define BUTTON_FILE "/sys/class/gpio/gpio459/value"
#define BUTTON_DIR  "/sys/class/gpio/gpio459/direction"
#define EXPORT 	 "/sys/class/gpio/export"
 
static void init_gpio (void)
{
  int fd;

  fd = open(EXPORT, O_WRONLY);
  if (fd < 0) {
    perror("error opening gpio export:");
    exit(-1);
  }

  write(fd, GPIO, strlen(GPIO));
  close(fd);

  fd = open(BUTTON_DIR, O_WRONLY);
  if (fd < 0) {
    perror("error opening gpio direction:");
    exit(-1);
  }

  write(fd, "in", 2);

  close(fd);

}

static void daemonize (void)
{
  int i;
  pid_t pid;
 
  if ((i = open("/dev/null", O_RDONLY)) != 0) {
    dup2(i, 0);
    close(i);
  }
  if ((i = open("/dev/null", O_WRONLY)) != 1) {
    dup2(i, 1);
    close(i);
  }
  if ((i = open("/dev/null", O_WRONLY)) != 2) {
    dup2(i, 2);
    close(i);
  }
 
  setsid();
 
  pid = fork();
 
  if (pid < 0) {
    perror("fork");
    exit(1);
  } else if (pid) { /* parent */
    exit(0);
  } else { /* child */
  }
}
 
 
static int state (void)
{
  char buf[32];
  int fd;
  int ret; 

  fd = open(BUTTON_FILE, O_RDONLY);
  if (fd < 0) {
    perror("open button");
    return -1;
  }

  read(fd, buf, 32);
	
  if (strncmp("1", buf, 1) == 0) {
    ret = 1;
  } else {
    ret = 0;
  }

  close(fd);

  return ret;

}

int main (int argc, char ** argv)
{
  init_gpio();
 
  int held, last, this;
  int long_press = 0;

  last = state();

  for (;;) {

    this = state();

    if (this == 0) {
        held++;
    }

    if (!long_press && (held > THRESH)) {
	printf("long hold\n");
	system("mcreset");
	long_press = 1;
    }

    if (last != this) {

        if (this == 1) {
           printf("released\n");
	   if (long_press) {
	       printf("factory reset\n");
               system("python /root/bramble/files/arch/bin/factory_reset.py");
	       system("systemctl reboot");
           } else {
               printf("reboot\n");
               system("mcreset");
	       system("systemctl reboot");
           }
           held = 0;
           long_press = 0;
        } else {
           printf("pressed\n");
        }

        last = this;   

    }

    usleep(SLEEP_TIME);

  }

}
