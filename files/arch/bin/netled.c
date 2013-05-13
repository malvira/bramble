#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
 
#define RX_FILE "/sys/class/net/eth0/statistics/rx_bytes"
#define TX_FILE "/sys/class/net/eth0/statistics/tx_bytes"
#define OPERSTATE "/tmp/dhcp-state"

#define ON "0"
#define OFF "1"

#define RATE (5 * 1024)

#define GPIO     "453" 
#define LED_FILE "/sys/class/gpio/gpio453/value"
#define LED_DIR  "/sys/class/gpio/gpio453/direction"
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

  fd = open(LED_DIR, O_WRONLY);
  if (fd < 0) {
    perror("error opening gpio direction:");
    exit(-1);
  }

  write(fd, "out", 3);

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
 
 
static int operstate (void)
{
  char buf[32];
  int fd;
  int ret; 

  fd = open(OPERSTATE, O_RDONLY);
  if (fd < 0) {
    perror("open operstate");
    return -1;
  }

  read(fd, buf, 32);
	
  if (strncmp("good", buf, 4) == 0) {
    ret = 1;
  } else {
    ret = 0;
  }

  close(fd);

  return ret;

}

static unsigned long long update (void)
{
  char buf[32];
  int fd;
  unsigned long long ret;
 
  /* RX */
  fd = open(RX_FILE, O_RDONLY);
  if (fd < 0) {
    perror("open rx");
    return -1;
  }
 
  read(fd, buf, 32);
  ret = atoll(buf);
 
  if(close(fd) < 0) {
    perror("close:");
  }

  /* TX */
  fd = open(TX_FILE, O_RDONLY);
  if (fd < 0) {
    perror("open tx");
    return -1;
  }
 
  read(fd, buf, 32);
  ret += atoll(buf);
 
  if(close(fd) < 0) {
    perror("close:");
  }

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

  init_gpio();
 
  led_fd = open(LED_FILE, O_WRONLY);
  if (led_fd < 0) {
    perror("open led");
    exit(-1);
  }
 
//  daemonize();
 
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
 
  if(close(led_fd) < 0) {
    perror("close:");
  }
}
