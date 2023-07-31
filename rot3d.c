
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
/* 3D Rotation */
void rot3d (float *image,float *rotimg,long sx,long sy,long sz,float *p_euler_A,char ip,float px,float py,float pz, int euler_dim)
{
long  sx_1, sy_1, sz_1;	/* highest pixels */
long  sxy;
long  i, j, k;		/* loop variables */
long  pi, pj, pk;	/* loop variables */
float r_x, r_y, r_z;    /* rotated coordinates */
float rm00, rm01, rm02, rm10, rm11, rm12, rm20, rm21, rm22; 	/* rotation matrix */
float sinphi, sinpsi, sintheta;	/* sin of rotation angles */
float cosphi, cospsi, costheta;	/* cos of rotation angles */
long  floorx, floory, floorz;		/* rotated coordinates as integer */
float vx1, vx2;		
float vy1, vy2;			/* difference between floorx & r_x , ... */
float vz1, vz2;
float AA, BB, CC, DD;   	/* interpolation values */
long  iindex;			/* index of pixel in image vector */
long  index1, index2, index3, index4, index5, index6;
float img0, img1, img2, img3, img4, img5, img6;
float angles[] = { 0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330 };
float angle_cos[16];
float angle_sin[16];
float phi,psi,theta;


phi=p_euler_A[0];
psi=p_euler_A[1];
theta=p_euler_A[2];

angle_cos[0]=1;
angle_cos[1]=sqrt(3)/2;
angle_cos[2]=sqrt(2)/2;
angle_cos[3]=0.5;
angle_cos[4]=0;
angle_cos[5]=-0.5;
angle_cos[6]=-sqrt(2)/2;
angle_cos[7]=-sqrt(3)/2;
angle_cos[8]=-1;
angle_cos[9]=-sqrt(3)/2;
angle_cos[10]=-sqrt(2)/2;
angle_cos[11]=-0.5;
angle_cos[12]=0;
angle_cos[13]=0.5;
angle_cos[14]=sqrt(2)/2;
angle_cos[15]=sqrt(3)/2;
angle_sin[0]=0;
angle_sin[1]=0.5;
angle_sin[2]=sqrt(2)/2;
angle_sin[3]=sqrt(3)/2;
angle_sin[4]=1;
angle_sin[5]=sqrt(3)/2;
angle_sin[6]=sqrt(2)/2;
angle_sin[7]=0.5;
angle_sin[8]=0;
angle_sin[9]=-0.5;
angle_sin[10]=-sqrt(2)/2;
angle_sin[11]=-sqrt(3)/2;
angle_sin[12]=-1;
angle_sin[13]=-sqrt(3)/2;
angle_sin[14]=-sqrt(2)/2;
angle_sin[15]=-0.5;

sx_1 = sx - 0.5;
sy_1 = sy - 0.5;
sz_1 = sz - 0.5;

for (i=0, j=0 ; i<16; i++)
{
	if (angles[i] == phi ) 
	{ 
		cosphi = angle_cos[i];
		sinphi = angle_sin[i];
		j = 1;
	}
}

if (j < 1) 
{ 
	phi = phi * M_PI / 180;
	cosphi=cos(phi);
	sinphi=sin(phi);
}

for (i=0, j=0 ; i<16; i++)
{
	if (angles[i] == psi ) 
	{
		cospsi = angle_cos[i];
		sinpsi = angle_sin[i];
		j = 1;
	}
}

if (j < 1) 
{ 
	psi = psi * M_PI / 180;
	cospsi=cos(psi);
	sinpsi=sin(psi);
}

for (i=0, j=0 ; i<16; i++)
{
	if (angles[i] == theta ) 
	{
		costheta = angle_cos[i];
		sintheta = angle_sin[i];
		j = 1;
	}
}

if (j < 1) 
{ 
	theta = theta * M_PI / 180;	
	costheta=cos(theta);
	sintheta=sin(theta);
}

/* calculation of rotation matrix */

if (euler_dim == 1)
{	
	rm00=cospsi*cosphi-costheta*sinpsi*sinphi;
	rm10=sinpsi*cosphi+costheta*cospsi*sinphi;
	rm20=sintheta*sinphi;
	rm01=-cospsi*sinphi-costheta*sinpsi*cosphi;
	rm11=-sinpsi*sinphi+costheta*cospsi*cosphi;
	rm21=sintheta*cosphi;
	rm02=sintheta*sinpsi;
	rm12=-sintheta*cospsi;
	rm22=costheta;
	/*printf("coeff: %f %f %f  %f %f %f  %f %f %f /n",rm00,rm10,rm20,rm01,rm11,rm21,rm02,rm12,rm22);*/
}
else
{
	rm00=p_euler_A[0];
	rm10=p_euler_A[1];
	rm20=p_euler_A[2];
	rm01=p_euler_A[3];
	rm11=p_euler_A[4];
	rm21=p_euler_A[5];
	rm02=p_euler_A[6];
	rm12=p_euler_A[7];
	rm22=p_euler_A[8];
}


if (ip == 'l') 
{
	sx_1 = sx - 1;
	sy_1 = sy - 1;
	sz_1 = sz - 1;
	sxy = sx * sy;
	index1 = sx;
	index2 = sx + 1;
	index3 = sxy;
	index4 = sxy + 1;
	index5 = sx + sxy;
	index6 = sx + sxy + 1;

	for (k=0; k < sz; k++)
	{	
		for (j=0; j < sy; j++)
		{
			for (i=0; i < sx; i++) 
			{
				pi = i-px;
				pj = j-py;
				pk = k-pz;

				/* transformation of coordinates */
				r_x = px + rm00 * pi + rm10 * pj + rm20 * pk;
				if (r_x < 0 || r_x > sx_1 ) 
				{
					*rotimg++ = 0;   /* this pixel was not inside the image */
					continue;
				} 
				r_y = py + rm01 * pi + rm11 * pj + rm21 * pk;
				if (r_y < 0 || r_y > sy_1 ) 
				{
					*rotimg++ = 0;
					continue;
				} 
				r_z = pz + rm02 * pi + rm12 * pj + rm22 * pk;
				if (r_z < 0 || r_z > sz_1 ) 
				{
					*rotimg++ = 0;
					continue;
				} 

				/* Interpolation */
				floorx = r_x;
				vx2 = r_x - floorx;
				vx1 = 1 - vx2;
				floory = r_y;
				vy2 = r_y - floory;
				vy1 = 1 - vy2;
				floorz = r_z;
				vz2 = r_z - floorz;
				vz1 = 1 - vz2;

				/* the following section detects border pixels to avoid exceeding dimensions */
				iindex = floorx + floory * sx + floorz * sxy;
				img0 = img1 = img2 = img3 = img4 = img5 = img6 = 1;
				if (floorx == sx-1)
				{
					img0 = img2 = img4 = img6 = 0;
				}
				if (floory == sy-1)
				{
					img1 = img2 = img5 = img6 = 0;
				}
				if (floorz == sz-1)
				{
					img3 = img4 = img5 = img6 = 0;
				}

				if (img0==1) 
				{ 
					img0=image[iindex + 1];
				}
				if (img1==1)
				{
					img1=image[iindex + index1];
				}
				if (img2==1) 
				{
					img2=image[iindex + index2];
				}
				if (img3==1) 
				{
					img3=image[iindex + index3];
				}
				if (img4==1) 
				{
					img4=image[iindex + index4];
				}
				if (img5==1)
				{ 
					img5=image[iindex + index5];
				}
				if (img6==1) 
				{
					img6=image[iindex + index6];
				}

				/* interpolation */
				AA = image[iindex] + (img0 - image[iindex]) * vx2;
				BB = img1 * vx1 + img2 * vx2;
				CC = img3 * vx1 + img4 * vx2;
				DD = img5 * vx1 + img6 * vx2;
				*rotimg++ = (AA * vy1 + BB * vy2) * vz1 + (CC * vy1 + DD * vy2) * vz2;
			}
		}
	}
}

}

