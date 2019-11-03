#include "main.h"
#include "unistd.h"
//
int fmsock,fmdst,fftsock,fftdst;
int sin_size;
struct sockaddr_in my_addr,fft_addr;
struct sockaddr_in their_addr,fft_their;

#define SERVER_ADDR "192.168.3.120"
int main()
{
	void *retval;
	pthread_t thread_command;
	pthread_t thread_client;
	int thread_cli;
	int arg[2],ret;
	int thread_cmd;
	arg[0]=1;
	arg[1]=0;
	
	fmsock=socket(AF_INET,SOCK_STREAM,0);
	fftsock=socket(AF_INET,SOCK_STREAM,0);
	my_addr.sin_family=AF_INET;
	my_addr.sin_port=htons(NET_PORT);
	my_addr.sin_addr.s_addr=inet_addr(SERVER_ADDR);
	
	fft_addr.sin_family=AF_INET;
	fft_addr.sin_port=htons(FFT_PORT);
	fft_addr.sin_addr.s_addr=inet_addr(SERVER_ADDR);
	//first connect fft then fm finally cmd
	ret=connect(fftsock, (struct sockaddr *)&fft_addr, sizeof(fft_addr));
	printf("connect fft %d \n",ret);
	ret=connect(fmsock, (struct sockaddr *)&my_addr, sizeof(my_addr));
	printf("connect fm  %d \n",ret);
	thread_cmd = pthread_create(&thread_command, NULL, (void *)&control_process, (void *)arg);

	while(arg[0])
	{

			if(arg[1]==1)
				ffts(&arg[1],fftsock,fft_cli_num);
			else if(arg[1]==2)
				fmdm(&arg[1],fmsock,fm_cli_num);
	}
	printf("bye bye!");
	exit(0);
}
/*函数 gsend()

dst 目标客户集

val 欲发送数据

len 发送数据长度

num 客户数量

*/
void gsend(int* dst,void* val,int len,int num)
{
	int i;
	int ret;
	for(i=0;i<num;i++)
	{
		if(dst[i])
		{
			ret=send(dst[i],val,len,0);
			if(ret<0)
				dst[i]=0;//销毁中断的客户
		}
		
	}
}
/*函数 get_client()
独立线程 等待用户接入并加入用户集

*/
void get_client()
{
	while (1&&fft_cli_num<MAX_CLI&&fm_cli_num<MAX_CLI)
	{
		printf("waitting for other client %d  %d\n",fft_cli_num,fm_cli_num);
		fmdst=accept(fmsock,(struct sockaddr*)&their_addr,&sin_size);
		if(fmdst)
		{
			fm_cli[fm_cli_num++]=fmdst;
			printf("find fm client %d\n",fmdst);
		}
		fftdst=accept(fftsock,(struct sockaddr*)&fft_their,&sin_size);
		if(fftdst)
		{
			fft_cli[fft_cli_num++]=fftdst;
			printf("find fft client %d\n",fftdst);
		}
	}
	printf("\nreach max client....exit\n");
	exit(0);
}
/*函数 control_process()
独立线程 接收及解析命令

解析结果通过 arg[1] 保存，并在主函数中用以改变运行状态

*/
void control_process(void *arg)
{
	pthread_t thread_client;
	// create socket project
	int sockcmd=socket(AF_INET,SOCK_STREAM,0);
	int thread_cli;
	// set socket attr
	struct sockaddr_in addr;
	addr.sin_family =AF_INET;
	addr.sin_port =htons(CRTL_PORT);
	addr.sin_addr.s_addr=inet_addr(SERVER_ADDR);
	struct sockaddr_in cli;
	socklen_t len=sizeof(cli);
	//bind address
	int cmd_ret =connect(sockcmd, (struct sockaddr *)&addr, sizeof(addr));
	int *buf;
	buf=(int *)malloc(8);
	fm_cli_num=1;
	fft_cli_num=1;
	if(0>cmd_ret)
	{
		printf("connect cmd port failed \n");
		return ;
	}
	printf("start cmd detect loop\n");
	while(((int *)arg)[0])//main loop
	{
		recv(sockcmd,buf,4,0);//接受命令
		short cmd,data;
		cmd=*buf>>16;
		data=*buf&0xffff;
		printf("cmd recv cmd:%d  data:%d  arg[0]:%d\n",cmd,data,((int *)arg)[0]);
		switch (cmd)//解析命令
		{
			case 1:
			{
				set_dev_paths("ad9361-phy");
				write_devattr_int("out_altvoltage0_RX_LO_frequency", data*100000+88000000);//data*0.1M +88M
				printf("set freq to %d",data*100000+88000000);
				break;//set fm freq
			}
			case 3:((int *)arg)[1]=2;break;//start fmod 
			case 4:((int *)arg)[1]=1;break;//start fft
			case 5:((int *)arg)[1]=0;send(fft_cli,"\xaa\xbb\xcc\xdd",4,0);break;//kill sub
			case 6:((int *)arg)[0]=0;exit(0);break;//kill all
			case 7:
			{
				
				((int *)arg)[1]=0;
				printf("reserve option!!\n");
				break;
			}
		}
    }
    close(sockcmd);
}
