/************* UDP CLIENT CODE *******************/

#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>

#define STR(num) #num

int main(){
  int clientSocket, portNum, nBytes;
  char buffer[530];
  //unsigned short  buffer[512];
  struct sockaddr_in serverAddr;
  socklen_t addr_size;

  /*Create UDP socket*/
  clientSocket = socket(AF_INET, SOCK_DGRAM, 6454);

  while(1){
    nBytes = recvfrom(clientSocket,buffer,530,0,NULL, NULL);

    printf(STR(buffer)": \n");
    unsigned int value = 0;
    int c = 0;
    
    for (int i = 0; i < 530; ++i) {
        c |= ((0xff & value) << 24);
        value = buffer[i];
        printf("%02X", (char)value);
  
    }
    printf("\b\b\n");

  }
  return 0;
}
