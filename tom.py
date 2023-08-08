# Matlab TOM Toolbox functions converted into Python

# import python packages
import os
import shutil
import subprocess
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from scipy.fft import fftn, fftshift, ifftn, ifftshift
from skspatial.objects import Points
from skimage.morphology import remove_small_objects
import matplotlib.pyplot as plt
import starfile
import mrcfile

# import C-file
import ctypes
from ctypes import *
so_file = os.getcwd() + "/rot3d.so"
rot_function = CDLL(so_file)

# wiener filter functions
def wienergraph(angpix, defocus, snrfalloff, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton):
    highpass = np.arange(0, 1 + 1 / 2047, 1 / 2047)
    highpass = np.minimum(1, highpass / highpassnyquist) * np.pi
    highpass = 1 - np.cos(highpass)

    snr = np.exp((np.arange(0, -1 - (1/2047), -1 / 2047)) * snrfalloff * 100 / angpix) * 1000 * highpass
    if phasebutton == True:
        ctf = np.abs(ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))
    else:
        ctf = (ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))

    wiener = []
    for c, s in zip(ctf, snr):
        if s == 0:
            v = 0
        else:
            v = c / (c * c + 1 / s)
        wiener.append(v)
    plt.close()
    plt.plot(np.arange(0, 1 + 1 / 2047, 1 / 2047), wiener)
    plt.grid(True)
    plt.title('Wiener Function')
    plt.ylabel('Wiener Filter Function')

def deconv_tomo(vol, angpix, defocus, snrfalloff, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton):
    highpass = np.arange(0, 1 + 1 / 2047, 1 / 2047)
    highpass = np.minimum(1, highpass / highpassnyquist) * np.pi
    highpass = 1 - np.cos(highpass)

    snr = np.exp((np.arange(0, -1 - (1/2047), -1 / 2047)) * snrfalloff * 100 / angpix) * 1000 * highpass
    if phasebutton == True:
        ctf = np.abs(ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))
    else:
        ctf = (ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))

    wiener = []
    for c, s in zip(ctf, snr):
        if s == 0:
            v = 0
        else:
            v = c / (c * c + 1 / s)
        wiener.append(v)

    s1 = -np.floor(vol.shape[0] / 2)
    f1 = s1 + vol.shape[0] - 1
    s2 = -np.floor(vol.shape[1] / 2)
    f2 = s2 + vol.shape[1] - 1
    s3 = -np.floor(vol.shape[2] / 2)
    f3 = s3 + vol.shape[2] - 1

    x, y, z = np.mgrid[s1:f1+1, s2:f2+1, s3:f3+1]
    x = x / np.abs(s1)
    y = y / np.abs(s2)
    z = z / max(1, np.abs(s3))
    r = np.sqrt(x**2 + y**2 + z**2)
    r = np.minimum(1, r)
    r = ifftshift(r)
    x = np.arange(0, 1 + 1/2047, 1 / 2047)

    ramp = np.interp(r, x, wiener)
    deconv = np.real(ifftn(fftn(vol.astype(np.float32)) * ramp))
    return deconv

def ctf1d(length, pixelsize, voltage, cs, defocus, amplitude_contrast, phase_shift, bfactor):
    ny = 1 / (pixelsize)
    lambda_ = 12.2643247 / np.sqrt(voltage * (1.0 + voltage * 0.978466e-6)) * 1e-10
    lambda2 = lambda_ * 2

    points = np.arange(0, length)
    points = points / (2 * length) * ny
    k2 = points ** 2
    term1 = lambda_**3 * cs * k2**2

    w = np.pi / 2 * (term1 + lambda2 * defocus * k2) - phase_shift

    acurve = np.cos(w) * amplitude_contrast
    pcurve = -np.sqrt(1 - amplitude_contrast**2) * np.sin(w)
    bfactor_term = np.exp(-bfactor * k2 * 0.25)

    ctf = (pcurve + acurve) * (bfactor_term)

    return ctf


# create mask functions
def spheremask(vol, radius, boxsize, sigma=0, center=None):
    vol = vol.reshape((int(boxsize[0]), int(boxsize[1]), int(boxsize[2])))
    if center == None:
        center = [np.floor(vol.shape[0] / 2) + 1, np.floor(vol.shape[1] / 2) + 1, np.floor(vol.shape[2] / 2) + 1]
    x, y, z = np.mgrid[0:vol.shape[0], 0:vol.shape[1], 0:vol.shape[2]]
    x = np.sqrt((x + 1 - center[0])**2 + (y + 1 - center[1])**2 + (z + 1 - center[2])**2)
    ind = np.where(x >= radius)
    mask = np.ones(vol.shape, dtype=np.float32)
    mask[ind] = 0

    if sigma > 0:
        mask[ind] = np.exp(-((x[ind] - radius) / sigma)**2)
        ind = np.where(mask < np.exp(-2))
        mask[ind] = 0

    vol = vol * mask
    return vol

def cylindermask(vol, radius, sigma, center):
    x, y = np.mgrid[0:vol.shape[0], 0:vol.shape[1]]
    x = np.sqrt((x + 1 - center[0])**2 + (y + 1 - center[1])**2)
    ind = np.where(x >= radius)
    mask = np.ones((vol.shape[0], vol.shape[1]), dtype=np.float32)
    mask[ind] = 0

    if sigma > 0:
        mask[ind] = np.exp(-((x[ind] - radius) / sigma)**2)
        ind = np.where(mask < np.exp(-2))
        mask[ind] = 0

    for iz in range(vol.shape[2]):
        vol[:, :, iz] = vol[:, :, iz] * mask
    return vol

# 3D Signal Subtraction Functions
def readList(listName, pxsz, extstar, angles):
    _, ext = os.path.splitext(listName)
    exstar = "_" + extstar
    if ext == '.star':
        star_data = starfile.read(listName)["particles"]
        list_length = len(star_data)

        new_star = starfile.read(listName)
        def replaceName(s):
            s = s.split("/")
            s.insert(-1, extstar)
            s = '/'.join(s)
            return s
        df = pd.DataFrame.from_dict(new_star["particles"])
        df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))

        # modifies starfile according to rotation type
        if angles != []:
            if len(angles) == 0: # star
                zeros = np.zeros(df.loc[:, "rlnAngleRot":"rlnOriginZAngst" ].shape)
                df.loc[:, "rlnAngleRot":"rlnOriginZAngst" ] = zeros
            
            if len(angles) == 3: # manual
                if angles[0] == 0 and angles[1] == 0: # X-axis  corresponds to  phi=0   psi=0   theta=alpha
                    df.loc[:, "rlnAngleRot"] += angles[2]
                if angles[0] == 270 and angles[1] == 90: # Y-axis  corresponds to  phi=270   psi=90  theta=alpha
                    df.loc[:, "rlnAngleTilt"] += angles[2]  
                if angles[1] == 0 and angles[2] == 0: # Z-axis  corresponds to  phi=alpha   psi=0   theta=0
                    df.loc[:, "rlnAnglePsi"] += angles[0]
            
        new_star["particles"] = df
        starfile.write(new_star, _ + exstar + ".star", overwrite=True)
        new_star_name = _ + exstar + ".star"

        Align = allocAlign(list_length)
        fileNames = []
        PickPos = np.empty(shape=(3, list_length))
        shifts = np.empty(shape=(3, list_length))
        angles = np.empty(shape=(3, list_length))
        for i in range(list_length):
            fileNames.append(star_data['rlnImageName'][i])
            PickPos[:,i] = [star_data['rlnCoordinateX'][i], star_data['rlnCoordinateY'][i], star_data['rlnCoordinateZ'][i]]
            shifts[:,i] = [-float(star_data['rlnOriginXAngst'][i]) / pxsz, -float(star_data['rlnOriginYAngst'][i]) / pxsz, -float(star_data['rlnOriginZAngst'][i]) / pxsz]
            euler_angles = eulerconvert_xmipp(star_data['rlnAngleRot'][i], star_data['rlnAngleTilt'][i], star_data['rlnAnglePsi'][i])
            angles[:,i] = [euler_angles[0], euler_angles[1], euler_angles[2]]
            
            Align[i]["Filename"] = fileNames[i]
            Align[i]["Angle"]["Phi"] = angles[0, i]
            Align[i]["Angle"]["Psi"] = angles[1, i]
            Align[i]["Angle"]["Theta"] = angles[2, i]
            Align[i]["Shift"]["X"] = shifts[0, i]
            Align[i]["Shift"]["Y"] = shifts[1, i]
            Align[i]["Shift"]["Z"] = shifts[2, i]
    else:
        raise ValueError("Unsupported file extension.")
    return fileNames, angles, shifts, list_length, PickPos, new_star_name

def allocAlign(num_of_entries):
    Align = []
    for i in range(num_of_entries):
        align_entry = {
            'Filename': '',
            'Tomogram': {
                'Filename': '',
                'Header': '',
                'Position': {
                    'X': -1,
                    'Y': -1,
                    'Z': -1
                },
                'Regfile': '',
                'Offset': [0, 0, 0],
                'Binning': 0,
                'AngleMin': 0,
                'AngleMax': 0
            },
            'Shift': {
                'X': 0,
                'Y': 0,
                'Z': 0
            },
            'Angle': {
                'Phi': 0,
                'Psi': 0,
                'Theta': 0,
                'Rotmatrix': []
            },
            'CCC': -1,
            'Class': -1,
            'ProjectionClass': 0,
            'NormFlag': 0,
            'Filter': [0, 0]
        }
        Align.append(align_entry)
    return Align

def eulerconvert_xmipp(rot, tilt, psi):
    rot2 = -psi * np.pi / 180
    tilt = -tilt * np.pi / 180
    psi = -rot * np.pi / 180
    rot = rot2

    rotmatrix = np.dot(
        np.dot(
            np.array([[np.cos(rot), -np.sin(rot), 0],
                      [np.sin(rot), np.cos(rot), 0],
                      [0, 0, 1]]),
            np.array([[np.cos(tilt), 0, np.sin(tilt)],
                      [0, 1, 0],
                      [-np.sin(tilt), 0, np.cos(tilt)]])),
        np.array([[np.cos(psi), -np.sin(psi), 0],
                  [np.sin(psi), np.cos(psi), 0],
                  [0, 0, 1]])
    )

    euler_out = np.zeros(3)
    euler_out[0] = np.arctan2(rotmatrix[2, 0], rotmatrix[2, 1]) * 180 / np.pi
    euler_out[1] = np.arctan2(rotmatrix[0, 2], -rotmatrix[1, 2]) * 180 / np.pi
    euler_out[2] = np.arccos(rotmatrix[2, 2]) * 180 / np.pi
    euler_out[euler_out < 0] += 360

    if -(rotmatrix[2, 2] - 1) < 10e-8:
        euler_out[2] = 0
        euler_out[1] = 0
        euler_out[0] = np.arctan2(rotmatrix[1, 0], rotmatrix[0, 0]) * 180 / np.pi
    return euler_out

def processParticle(filename,tmpAng,tmpShift,maskh1,PickPos,offSetCenter,boxsize,filter,grow,normalizeit, sdRange, sdShift,blackdust,whitedust,shiftfil,randfilt,permutebg):
    volTmp = mrcfile.read(filename)
    maskh1Trans = shift(rotate(maskh1, tmpAng, boxsize), tmpShift.conj().transpose())
    maskh1Trans = maskh1Trans > 0.14
    vectTrans = pointrotate(offSetCenter,tmpAng[0],tmpAng[1],tmpAng[2])+tmpShift.conj().transpose()
    posNew=(np.round(vectTrans)+PickPos).conj().transpose()

    # cut and filter
    outH1 = volTmp
    if filter == True:
        if shiftfil == True:
            outH1 = maskWithFil(outH1,maskh1Trans, sdRange, sdShift,blackdust,whitedust)
        elif randfilt == True:
            outH1 = randnoise_filt(outH1,maskh1Trans,'', 0, sdRange,blackdust,whitedust)
    if permutebg == True:
        outH1 = permute_bg(outH1, maskh1Trans, boxsize, '', grow, 5, 3)

    if normalizeit == True:
        input = outH1
        inputShape = input.shape
        inmax = np.max(input)
        inmin = np.min(input)
        range = inmax - inmin
        input = ((input-inmin) / range - .5) * 2
        indd = np.flatnonzero(maskh1Trans < 0.1)
        ind_rand = np.random.permutation(len(indd))
        input = input.flatten()
        input[indd] = input[indd[ind_rand]]
        input = input.reshape(inputShape)
        outH1 = input

    return outH1, posNew

def shift(im, delta):
    dimx, dimy, dimz = im.shape
    if delta.ndim > 1:
        delta = delta.flatten()

    # MeshGrid with the sampling points of the image
    x, y, z = np.mgrid[-np.floor(dimx/2):-np.floor(dimx/2)+dimx, 
                       -np.floor(dimy/2):-np.floor(dimy/2)+dimy, 
                       -np.floor(dimz/2):-np.floor(dimz/2)+dimz]

    indx = np.where([dimx, dimy, dimz] == 1)[0]
    delta[indx] = 0
    delta /= [dimx, dimy, dimz]
    x = delta[0] * x + delta[1] * y + delta[2] * z
    im = fftn(im)
    im = np.real(ifftn(im * np.exp(-2j * np.pi * ifftshift(x))))
    return im


def rotate(input, angles, boxsize):
    # This is a 3d Euler rotation around (zxz)-axes
    # with Euler angles (psi,theta,phi)
    center = np.ceil(np.array(input.shape) / 2)
    ip = 'l'
    taper = 'no'
    in_array = input
    in_array = in_array.astype(np.float32)
    euler_angles = np.array(angles)
    euler_angles = euler_angles.astype(np.float32)
    sx = int(boxsize[0])
    sy = int(boxsize[1])
    sz = int(boxsize[2])
    px = float(center[0])
    py = float(center[1])
    pz = float(center[2])
    
    if taper != 'taper':
        out = np.zeros_like(in_array, dtype=np.float32)
        pointer_in = np.ctypeslib.ndpointer(shape = in_array.shape, dtype = np.float32)
        pointer_out = np.ctypeslib.ndpointer(shape = out.shape, dtype = np.float32)
        pointer_ang = np.ctypeslib.ndpointer(shape = euler_angles.shape, dtype = np.float32)
        rot_function.rot3d.argtypes = (pointer_in, pointer_out, ctypes.c_long, ctypes.c_long, ctypes.c_long, pointer_ang, ctypes.c_wchar, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_int)
        rot_function.rot3d.restype = None
        # call C-Function to do the calculations
        rot_function.rot3d(in_array, out, sx, sy, sz, euler_angles, ip, px, py, pz, 1)
        out = out.astype(np.float64)
    
    return out

def tom_taper(in_data, new_size):
    if len(new_size) == 2:
        new_size.append(1)

    out = np.zeros(new_size)
    out = paste(out, in_data, np.round(((np.array(out.shape) - np.array(in_data.shape)) / 2) + 1))

    for z in range(1, new_size[2] + 1):
        diff_z = np.round((new_size[2] - in_data.shape[2]) / 2)
        if z > diff_z and z <= in_data.shape[2] + diff_z:
            im = in_data[:, :, z - diff_z - 1]
            out_sl = out[:, :, z - 1]

            a = im[:, 0]
            b = im[:, im.shape[1] - 1]
            c = im[0, :]
            d = im[im.shape[0] - 1, :]

            diff_hor = np.round((new_size[0] - im.shape[0]) / 2)
            diff_vert = np.round((new_size[1] - im.shape[1]) / 2)
            stop_up = diff_vert
            start_down = out.shape[1] - diff_vert

            for i in range(1, new_size[0] + 1):
                if i <= diff_hor or i > (im.shape[0] + diff_hor):
                    if i < diff_hor:
                        val_up = a[0]
                        val_low = b[0]
                    else:
                        val_up = a[a.shape[0] - 1]
                        val_low = b[b.shape[0] - 1]
                else:
                    val_up = a[i - diff_hor - 1]
                    val_low = b[i - diff_hor - 1]

                out_sl[i - 1, :stop_up] = val_up
                out_sl[i - 1, start_down:] = val_low

            stop_left = diff_hor
            start_right = out.shape[0] - diff_hor

            for i in range(1, new_size[1] + 1):
                if i > diff_vert and i <= (im.shape[1] + diff_vert):
                    out_sl[:stop_left, i - 1] = c[i - diff_vert - 1]
                    out_sl[start_right:, i - 1] = d[i - diff_vert - 1]

            out[:, :, z - 1] = out_sl

    if new_size[2] == 1:
        return out
    for z in range(1, new_size[2] + 1):
        diff_z = np.round((new_size[2] - in_data.shape[2]) / 2)
        if z <= diff_z or z >= in_data.shape[2] + diff_z:
            if z <= diff_z:
                out[:, :, z - 1] = out[:, :, diff_z]
            else:
                out[:, :, z - 1] = out[:, :, diff_z + in_data.shape[2] - 1]
    return out
    
def paste(a, b, coord):
    dims = b.shape
    s1, s2, s3 = a.shape
    
    if s3 == 1:
        if coord[0] > s1 or coord[1] > s2:
            raise ValueError('Improper Selection of Starting Pixel')
        elif coord[0] <= 0 or coord[1] <= 0:
            if coord[0] <= 0 and coord[1] > 0:
                if coord[0] + dims[0] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                elif coord[1] + dims[1] - 1 > s2:
                    a[0:(coord[0] + dims[0] - 1), coord[1]:s2] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1)]
                else:
                    a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1)] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1]]
            elif coord[0] > 0 and coord[1] <= 0:
                if coord[1] + dims[1] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                elif coord[0] + dims[0] - 1 > s1:
                    a[coord[0]:s1, 0:(coord[1] + dims[1] - 1)] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1]]
                else:
                    a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1)] = b[0:dims[0], (abs(coord[1]) + 1):dims[1]]
            elif coord[0] <= 0 and coord[1] <= 0:
                if coord[0] + dims[0] - 1 < 1 or coord[1] + dims[1] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                else:
                    a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1)] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1]]
        else:
            if (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1)] = b
            elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1)] = b[0:(1 + s1 - coord[0]), 0:dims[1]]
            elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2] = b[0:dims[0], 0:(s2 - coord[1] + 1)]
            elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                a[coord[0]:s1, coord[1]:s2] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1)]
    else:
        if coord[0] > s1 or coord[1] > s2 or coord[2] > s3:
            raise ValueError('Improper Selection of Starting Pixel')
        elif coord[0] <= 0 or coord[1] <= 0 or coord[2] <= 0:
            if (coord[0] + dims[0] - 1) < 1 or (coord[1] + dims[1] - 1) < 1 or (coord[2] + dims[2] - 1) < 1:
                raise ValueError('Improper Selection of Starting Pixel')
        
        if coord[2] <= 0 and ((coord[2] + dims[2] - 1) <= s3):
            ad = abs(coord[2]) + 1
            for i in range(coord[2], coord[2] + dims[2]):
                if i <= 0:
                    continue
                else:
                    if coord[0] <= 0 and coord[1] > 0:
                        if (coord[1] + dims[1] - 1) > s2:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1), (i + ad)]
                        else:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1], (i + ad)]
                    elif coord[0] > 0 and coord[1] <= 0:
                        if (coord[0] + dims[0] - 1) > s1:
                            a[coord[0]:s1, 0:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1], (i + ad)]
                        else:
                            a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[0:dims[0], (abs(coord[1]) + 1):dims[1], (i + ad)]
                    elif coord[0] <= 0 and coord[1] <= 0:
                        a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1], (i + ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[:, :, (i + ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), 0:dims[1], (i + ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[0:dims[0], 0:(s2 - coord[1] + 1), (i + ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:s1, coord[1]:s2, i] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1), (i + ad)]
        elif coord[2] >= 1:
            ad = coord[2] - 1
            for i in range(coord[2], coord[2] + dims[2]):
                if i > s3:
                    continue
                else:
                    if coord[0] <= 0 and coord[1] > 0:
                        if (coord[1] + dims[1] - 1) > s2:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1), (i - ad)]
                        else:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1], (i - ad)]
                    elif coord[0] > 0 and coord[1] <= 0:
                        if (coord[0] + dims[0] - 1) > s1:
                            a[coord[0]:s1, 0:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1], (i - ad)]
                        else:
                            a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[0:dims[0], (abs(coord[1]) + 1):dims[1], (i - ad)]
                    elif coord[0] <= 0 and coord[1] <= 0:
                        a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1], (i - ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[:, :, (i - ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), 0:dims[1], (i - ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[0:dims[0], 0:(s2 - coord[1] + 1), (i - ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:s1, coord[1]:s2, i] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1), (i - ad)]
    return a

def cut_out(in_data, pos, size_c, fill_flag='no-fill'):
    if fill_flag != 'fill':
        fill_flag = 'no-fill'
    
    # kick out values < 1    
    pos = np.where(pos > 0, pos, 1)
    num_of_dim = in_data.ndim
    if in_data.shape[0] == 1:
        in_size = in_data.shape[1]
        num_of_dim = 1
    else:
        in_size = in_data.shape
        num_of_dim = in_data.ndim
    
    bound = np.zeros(3)
    
    if (pos[0] + size_c[0]) <= in_size[0]:
        bound[0] = pos[0] + size_c[0] - 1
    else:
        bound[0] = in_size[0]
    
    if num_of_dim > 1:
        if (pos[1] + size_c[1]) <= in_size[1]:
            bound[1] = pos[1] + size_c[1] - 1
        else:
            bound[1] = in_size[1]
    else:
        pos[1] = 0
        bound[1] = 0
    
    if num_of_dim > 2:
        if (pos[2] + size_c[2]) <= in_size[2]:
            bound[2] = pos[2] + size_c[2] - 1
        else:
            bound[2] = in_size[2]
    else:
        pos[2] = 0
        bound[2] = 0
    
    pos = np.round(pos).astype(int)
    bound = np.round(bound).astype(int)
    
    # cut it
    if num_of_dim > 1:
        out = in_data[pos[0]:(bound[0]+1), pos[1]:(bound[1]+1), pos[2]:(bound[2]+1)]
    else:
        out = in_data[pos[0]:bound[0]+1]
    
    return out
    
def pointrotate(r, phi, psi, the):
    phi = phi / 180 * np.pi
    psi = psi / 180 * np.pi
    the = the / 180 * np.pi

    matr = np.array([[np.cos(psi), -np.sin(psi), 0],
                     [np.sin(psi), np.cos(psi), 0],
                     [0, 0, 1]])

    matr = matr @ np.array([[1, 0, 0],
                            [0, np.cos(the), -np.sin(the)],
                            [0, np.sin(the), np.cos(the)]])

    matr = matr @ np.array([[np.cos(phi), -np.sin(phi), 0],
                            [np.sin(phi), np.cos(phi), 0],
                            [0, 0, 1]])

    r = matr @ r
    r = r.flatten()
    return r

def maskWithFil(input, mask, std2fil, std2shift, blackdust, whitedust):
    inputShape = input.shape
    input = input.flatten()
    indd = np.flatnonzero(mask < 0.1)
    ind_mean = np.mean(input[indd])
    ind_std = np.std(input[indd])

    if whitedust == True:
        indd2 = np.flatnonzero(input[indd] > (ind_mean + std2fil * ind_std))
        input[indd[indd2]] -= std2shift * ind_std

    if blackdust == True:
        indd2 = np.flatnonzero(input[indd] < (ind_mean - std2fil * ind_std))
        input[indd[indd2]] += std2shift * ind_std

    input = input.reshape(inputShape)
    return input

def randnoise_filt(input, mask, outputname, grow_rate, sdrange, blackdust, whitedust):
    inputShape = input.shape
    if grow_rate == 0:
        outmask = np.flatnonzero(mask < 0.1)
        input = input.flatten()
        outsmall = np.flatnonzero(input[outmask] < -sdrange)
        outlarge = np.flatnonzero(input[outmask] > sdrange)

        if whitedust == True:
            for i in range(len(outlarge)):
                input[outmask[outlarge[i]]] = np.random.normal(0, 1)

        if blackdust == True:
            for i in range(len(outsmall)):
                input[outmask[outsmall[i]]] = np.random.normal(0, 1)

    input = input.reshape(inputShape)
    return input

def permute_bg(input, mask, boxs, outputname='', grow_rate=0, num_of_steps=10, filt_cer=10, max_error = 10):

    center = [round(boxs[0]/2) + 1, round(boxs[1]/2) + 1, round(boxs[2]/2) + 1]

    if grow_rate == 0:
        indd = np.flatnonzero(mask < 0.1)
        ind_rand = np.random.permutation(len(indd))
        input = input.flatten()
        input[indd] = input[indd[ind_rand]]

    else:
        mask_tmp = mask
        smooth_ch = np.arange(100/num_of_steps, 100 + 100/num_of_steps, 100/num_of_steps)
        std_ch = np.arange(4/num_of_steps, 4 + 4/num_of_steps, 4/num_of_steps)
        filt_ch = np.round(np.arange(2, 0 - (2/num_of_steps), -(2/num_of_steps)))

        for i in range(num_of_steps):
            mask_old = mask_tmp
            mask_tmp = tom_grow_mask(mask_tmp, grow_rate, boxs, max_error, filt_cer)
            mask_old = mask_old.astype(int)
            mask_tmp = mask_tmp.astype(int)
            mask_diff = mask_tmp - mask_old

            indd = np.flatnonzero(mask_diff)
            ind_rand = np.random.permutation(len(indd))
            ind_rand2 = np.random.permutation(len(indd))
            cut_len = int(np.round(len(ind_rand) * (smooth_ch[i] / 100)))
            input = input.flatten()
            tmp_vox = input[indd[ind_rand[:cut_len]]]

            tmp_vox = np.array(tmp_vox)
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            
            input[indd[ind_rand2[:cut_len]]] = tmp_vox

            if filt_ch[i] == 0:
                in_f = input
            else:
                in_f = tom_filter(input, filt_ch[i], boxs, center)

            in_f = in_f.flatten()
            tmp_vox = in_f[indd[ind_rand[:cut_len]]]
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            input[indd[ind_rand2[:cut_len]]] = tmp_vox

        indd = np.array(np.flatnonzero(mask_tmp < 0.1))
        ind_rand = np.random.permutation(len(indd))
        input[indd] = input[indd[ind_rand]]

    input = input.reshape((int(boxs[0]), int(boxs[1]), int(boxs[2])))
    return input

def tom_grow_mask(mask, factor, boxsize, max_error=2, filter_cer=None):

    thr_inc = 0.1
    thr_tmp = 0.4

    org_num_of_vox = np.sum(mask > 0)
    dust_size = int(round(org_num_of_vox - (0.3 * org_num_of_vox)))

    max_itr = 1000

    mask_filt = tom_filter(mask, filter_cer, boxsize)
    for ii in range(1, 31):
        thr_inc /= ii
        thr_start = thr_tmp
        for i in range(1, max_itr + 1):
            thr_tmp = thr_start - (thr_inc * i)
            new_num = np.sum(remove_small_objects(mask_filt > thr_tmp, min_size = dust_size, connectivity=6))
            if new_num > (org_num_of_vox * factor):
                break
        act_error = ((new_num - (org_num_of_vox * factor)) / org_num_of_vox) * 100
        thr_tmp = thr_start - (thr_inc * (i - 1))
        if act_error < max_error:
            break
    new_mask = remove_small_objects(mask_filt > (thr_start - (thr_inc * i)), min_size = dust_size, connectivity = 6)
    
    return new_mask

def clean_stat(vox, nstd):
    mea_out = np.mean(vox)
    std_out = np.std(vox)

    idx = np.where((vox > (mea_out + (nstd * std_out))) + (vox < (mea_out - (nstd * std_out))))

    out = vox.copy()
    out[idx] = mea_out

    return out


def tom_filter(im, radius, boxsize, center=None, flag='circ'):
    if flag.lower() == 'circ':
        mask = np.ones_like(im)
        mask = spheremask(mask, radius, boxsize, 0, center)

    npix = np.sum(mask)
    mask = mask.astype(np.float32)
    im = im.astype(np.float32)
    im = im.reshape(mask.shape)
    im = np.real(fftshift(ifftn(fftn(mask) * fftn(im)) / npix))
    
    return im

# rotate subtomogram functions
def processParticler(filename, tmpAng, boxsize, shifts, shifton):
    volTmp = mrcfile.read(filename)
    storey = tmpAng[1]
    tmpAng[1] = tmpAng[0]
    tmpAng[0] = storey
    if shifton == True:
        outH1 = rotate(shift(volTmp, shifts), tmpAng, boxsize)
    else:
        outH1 = rotate(volTmp, tmpAng, boxsize)

#ATB    
# I commented out this call to cut_out. It makes the box smaller of there are values < 1. Does not make much sense and causes the subtomograms to get smaller!
#    outH1 = cut_out(outH1, np.array([0, 0, 0]), boxsize)
    return outH1

# CCC Calculations
def corr_wedge(a, b, wedge_a, wedge_b, boxsize):
    # mask creation
    mask = spheremask(np.ones_like(wedge_b), 30, boxsize)
    # apply wedge and mask to create wedge_all
    wedge_all = wedge_a * wedge_b * mask
    # calculate number of voxels
    n_all = np.count_nonzero(wedge_all)

    # normalize array a
    mn = np.mean(a)
    stdv = np.std(a)
    if stdv != 0:
        a = (a - mn) / stdv

    # normalize array b
    mn = np.mean(b)
    stdv = np.std(b)
    if stdv != 0:
        b = (b - mn) / stdv

    # compute correlation using FFT
    ccf = np.real(ifftshift(ifftn(fftn(b) * np.conj(fftn(a))))) / n_all
    return ccf

def ccc_loop(starf, cccvol1in, threshold, boxsize, zoomrange, mswedge):
    outputstar1 = starf.replace('.star', '_ccc_above.star')
    outputstar = starf.replace('.star', '_ccc_below.star')
    inputstar = starfile.read(starf)['particles']
    with mrcfile.open(cccvol1in) as invmrc:
        involbox = float(invmrc.header.nx)
    invol1 = mrcfile.read(cccvol1in)
    invol1 = np.transpose(invol1, (2,1,0))
    with mrcfile.open(mswedge, permissive=True) as wedmrc:
        wedgebox = float(wedmrc.header.nx)
    if involbox != wedgebox:
        print('Volume 1 and Missing Wedge box sizes do not match.')
        return
    wedge = mrcfile.read(mswedge)
    wedge = np.transpose(wedge, (2,1,0))
    direct = "/".join(starf.split("/")[:-1]) + '/'
    file_path = "calculate_ccc.txt" 
    ccc_file = open(direct + file_path, "w")

    # looping through each mrc, apply rots and shift, calculating ccc
    cccval = np.zeros(len(inputstar))
    for i in range(len(inputstar)):
        with mrcfile.open(direct + (inputstar['rlnImageName'][i])) as starmrc:
            starbox = float(starmrc.header.nx)
        if starbox != wedgebox:
            print('Star File Volume and Missing Wedge box sizes do not match.')
            continue
        invol2 = mrcfile.read(direct + (inputstar['rlnImageName'][i]))
        invol2 = np.transpose(invol2, (2,1,0))
        mwcorrvol2 = invol2 * wedge

        # pull in shifts and rotations from star file
        shiftOut = np.array([inputstar['rlnOriginXAngst'][i], inputstar['rlnOriginYAngst'][i],inputstar['rlnOriginZAngst'][i]]) / -2.62
        rotateOut = np.array([inputstar['rlnAnglePsi'][i],inputstar['rlnAngleTilt'][i], inputstar['rlnAngleRot'][i]]) * -1
        fixedRotations = eulerconvert_xmipp(rotateOut[0], rotateOut[1], rotateOut[2])
        rotVol = rotate(mwcorrvol2, fixedRotations.conj().transpose(), boxsize)
        shiftVol = shift(rotVol, shiftOut.conj().transpose())

        # apply rotations and shifts to missing wedge
        rotMw = rotate(wedge, fixedRotations.conj().transpose(), boxsize)
        shiftMw = shift(rotMw, shiftOut.conj().transpose())

        # calculate ccf and sum values
        ccf = corr_wedge(invol1, shiftVol, shiftMw, shiftMw, boxsize)
        left = round(boxsize[0]/2-zoomrange)
        right = round(boxsize[0]/2+zoomrange)
        cccval[i] = np.sum(ccf[left:right,left:right,left:right])
        #save cccval in text file (calculate_ccc.txt)
        ccc_file.write(f"{inputstar['rlnImageName'][i]}:  {cccval[i]}\n")

    removeList = np.flatnonzero(cccval > threshold)
    removeList1 = np.flatnonzero(cccval <= threshold)
    # create output REL3 star file with removeList values removed from star file
    shutil.copy(starf, outputstar)
    shutil.copy(starf, outputstar1)
    for x in range(len(removeList)):
        subprocess.run(['sed', '-i', '', '/' + inputstar['rlnImageName'][removeList[x]].replace('/', '\\/') + '/d', outputstar])
    for x in range(len(removeList1)):
        subprocess.run(['sed', '-i', '', '/' + inputstar['rlnImageName'][removeList1[x]].replace('/', '\\/') + '/d', outputstar1])
    return

# calculate angles 
def calcangles(dataframe):
    # split up dataframe columns
    Xmem = dataframe["Xmem"].astype(int).to_numpy()
    Ymem = dataframe["Ymem"].astype(int).to_numpy()
    Zmem = dataframe["Zmem"].astype(int).to_numpy()
    Xcen = dataframe["Xcen"].astype(int).to_numpy()
    Ycen = dataframe["Ycen"].astype(int).to_numpy()
    Zcen = dataframe["Zcen"].astype(int).to_numpy()
    #normalize cen values
    for i in range(0, len(Xmem)):
        Xcen[i] = Xcen[i]-Xmem[i]
        Ycen[i] = Ycen[i]-Ymem[i]
        Zcen[i] = Zcen[i] - Zmem[i]

    #put points into array, give them plotting param
    points = np.array([Xcen, Ycen, Zcen], dtype=float)
    points = (np.transpose(points))
    points = Points(points)
    vector_1 = [0, 0, 1]
    vector_2 = points
    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = 0
    newangs = np.zeros((len(points), 3))
    for w in range(0, len(points)):
        unit_vector_2 = vector_2[w] / np.linalg.norm(vector_2[w])
        dot_product = np.dot(unit_vector_2, unit_vector_1)
        angle = np.arccos(dot_product)
        crossprod = np.cross(unit_vector_2, unit_vector_1)
        axis = np.asarray(crossprod)
        axis = axis / np.sqrt(np.dot(axis, axis))
        r = R.from_rotvec(angle * axis)
        newangs[w, :] = r.as_euler('ZYZ', degrees=True)
        
    return newangs