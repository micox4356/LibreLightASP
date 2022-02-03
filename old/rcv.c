/************* UDP CLIENT CODE *******************/

#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>

#define STR(num) #num

int main(){
  int clientSocket, portNum, nBytes;
  char buffer[1024];
  struct sockaddr_in serverAddr;
  socklen_t addr_size;

  /*Create UDP socket*/
  clientSocket = socket(PF_INET, SOCK_DGRAM, 6454);

  /*Configure settings in address struct*/
  //serverAddr.sin_family = AF_INET;
  //serverAddr.sin_port = htons(7891);
  //serverAddr.sin_port = htons(6454);
  //serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
  //serverAddr.sin_addr.s_addr = inet_addr("2.0.0.1");
  //memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);  

  /*Initialize size variable to be used later on*/
  //addr_size = sizeof serverAddr;

  while(1){
    //printf("Type a sentence to send to server:\n");
    //fgets(buffer,1024,stdin);
    //printf("You typed: %s",buffer);

    nBytes = strlen(buffer) + 1;
    
    /*Send message to server*/
    //sendto(clientSocket,buffer,nBytes,0,(struct sockaddr *)&serverAddr,addr_size);

    /*Receive message from server*/
    //nBytes = recvfrom(clientSocket,buffer,1024,0,NULL, NULL);
    nBytes = recvfrom(clientSocket,buffer,512,0,NULL, NULL);
    //printf(": %s\n",nBytes);
    
    /*
    printf(": %s\n",(&buffer));
    
    int i = atoi(buffer);
    printf("%d\n", i);

    int ii;
    sscanf(buffer, "%d", &ii);
    */

    //# printf("%s\n", buffer);
    printf(STR(buffer)": ");
    for (int i = 0; i < 512; ++i) {
       //printf("%c, ", buffer[i]);
        //printf("%u, ", buffer[i]);
        //if( i > 500 & i < 512 ){
        printf("%i, ", buffer[i]);
	//}
    }
    printf("\b\b\n");
  
  /*
  unsigned int x = 0x76543210;
  char *c = (char*) &x;
 
  printf ("*c is: 0x%x\n", *c);
  if (*c == 0x10){
    printf ("Underlying architecture is little endian. \n");
  }else{
    printf ("Underlying architecture is big endian. \n");
  }
  */
  }

  return 0;
}
