#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
 
#define RX_FILE "/sys/class/net/eth0/statistics/rx_bytes"
#define TX_FILE "/sys/class/net/eth0/statistics/tx_bytes"
#define OPERSTATE "/sys/class/net/eth0/operstate"

#define ON "0"
#define OFF "1"

#define RATE (5 * 1024)
 
#define LED_FILE "/sys/class/gpio/gpio453/value"
 
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
 
 
static int operstate (void)
{
  char buf[32];
  int fd;
  fd = open(OPERSTATE, O_RDONLY);
  if (fd < 0) {
    perror("open");
    return -1;
  }

  read(fd, buf, 32);
	
  buf[2] = 0;
  if (strcmp("up", buf) == 0) {
    return 1;
  } else {
    return 0;
  }

  close(fd);

}

static unsigned long long update (void)
{
  char buf[32];
  int fd;
  unsigned long long ret;
 
  /* RX */
  fd = open(RX_FILE, O_RDONLY);
  if (fd < 0) {
    perror("open");
    return -1;
  }
 
  read(fd, buf, 32);
  ret = atoll(buf);
 
  close(fd);
 
  /* TX */
  fd = open(TX_FILE, O_RDONLY);
  if (fd < 0) {
    perror("open");
    return -1;
  }
 
  read(fd, buf, 32);
  ret += atoll(buf);
 
  close(fd);
   
  return ret;
}
 
static int led_fd;
 
static void blink (void)
{
  write(led_fd, ON, 1);
 
  usleep(20 * 1000);
 
  write(led_fd, OFF, 1);
}

static void slow_blink (void)
{
  write(led_fd, ON, 1);
 
  usleep(1000 * 1000);
 
  write(led_fd, OFF, 1);

  usleep(1000 * 1000);

  write(led_fd, ON, 1);
}
 
int main (int argc, char ** argv)
{
  unsigned long long newdata;
  unsigned long long olddata;
 
  led_fd = open(LED_FILE, O_WRONLY);
  if (led_fd < 0) {
    perror("open");
    exit(-1);
  }
 
  daemonize();
 
  olddata = 0;
  for (;;) {
    newdata = update();
 
    /* printf("%lld\n", newdata / RATE); */

    if (operstate() == 1) { 
        if ((newdata / RATE) != (olddata / RATE)) {
          blink();
        } else {
          write(led_fd, ON, 1);
        }
    } else {
      slow_blink();
    }

    olddata = newdata;
 
    usleep(50 * 1000);

  }
 
  close(led_fd);
}
