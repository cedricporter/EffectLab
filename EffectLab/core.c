#include <Python.h>
#include <stdio.h>
#include <math.h>
#include "ImPlatform.h" 

/* 1.1.9 pil */

typedef struct ImagingMemoryInstance* Imaging; 
typedef struct ImagingAccessInstance* ImagingAccess;
typedef struct ImagingPaletteInstance* ImagingPalette;

struct ImagingMemoryInstance {

    /* Format */
    char mode[6+1];	/* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "BGR;xy") */
    int type;		/* Data type (IMAGING_TYPE_*) */
    int depth;		/* Depth (ignored in this version) */
    int bands;		/* Number of bands (1, 2, 3, or 4) */
    int xsize;		/* Image dimension. */
    int ysize;

    /* Colour palette (for "P" images only) */
    ImagingPalette palette;

    /* Data pointers */
    UINT8 **image8;	/* Set for 8-bit images (pixelsize=1). */
    INT32 **image32;	/* Set for 32-bit images (pixelsize=4). */

    /* Internals */
    char **image;	/* Actual raster data. */
    char *block;	/* Set if data is allocated in a single block. */

    int pixelsize;	/* Size of a pixel, in bytes (1, 2 or 4) */
    int linesize;	/* Size of a line, in bytes (xsize * pixelsize) */

    /* Virtual methods */
    void (*destroy)(Imaging im);
};


struct ImagingAccessInstance {
  const char* mode;
  void* (*line)(Imaging im, int i, int j);
  void (*get_pixel)(Imaging im, int i, int j, void* pixel);
  void (*put_pixel)(Imaging im, int i, int j, const void* pixel);
};

struct ImagingPaletteInstance {

    /* Format */
    char mode[4+1];	/* Band names */

    /* Data */
    UINT8 palette[1024];/* Palette data (same format as image data) */

    INT16* cache;	/* Palette cache (used for predefined palettes) */
    int keep_cache;	/* This palette will be reused; keep cache */

};

typedef struct {
    PyObject_HEAD
    Imaging image;
    ImagingAccess access;
} ImagingObject;



/* 弧度变形 */
static int _radian_warp(PyObject *func, double x, double y, double *xnew, double *ynew)
{
    double phi,radius,radius2;
    PyObject *ret;

    radius2 = x * x + y * y;
    radius = sqrt(radius2);
    phi = atan2(y, x);

    if ((ret = PyObject_CallFunction(func, "dd", radius, phi)) == NULL)
    {
        return 0;
    }
    if (!PyArg_ParseTuple(ret, "dd", &radius, &phi))
    {
        return 0;
    } 
    Py_DECREF(ret);

    *xnew = radius * cos(phi);
    *ynew = radius * sin(phi);

    return 1;
}


/* 基于平移的变形 */
static int _xy_warp(PyObject *func, double x, double y, double *xnew, double *ynew)
{
    PyObject *ret;
    if ((ret = PyObject_CallFunction(func, "dd", x, y)) == NULL)
    {
        return 0;
    }
    if (!PyArg_ParseTuple(ret, "dd", xnew, ynew))
    {
        return 0;
    } 
    Py_DECREF(ret);

    return 1;
}


/* 镜头变形效果 */
static PyObject* _lens_warp(PyObject *self, PyObject *args, int (*warp)(PyObject*, double, double, double *, double*))
{
    PyObject *image;
    PyObject *newimage;
    ImagingObject *core;
    Imaging imIn, imOut;
    int i, j, ai, aj; 
    int found, rsum, gsum, bsum, asum;
    int antialias = 2;
    double xx, yy;
    int width, height;
    double i2, j2;
    double xnew, ynew;
    UINT8 *pixel; 
    int i3, j3;
    PyObject *func;
    PyObject *empty_color;
    int er, eg, eb, ea;

    if (!PyArg_ParseTuple(args, "OOiO", &image, &func, &antialias, &empty_color))
    {
        return NULL;
    } 

    if ((core = (ImagingObject *)PyObject_GetAttrString(image, "im")) == NULL)
    {
        return NULL;
    } 
    imIn = core->image;
    Py_DECREF(core);

    /* copy a new image */
    newimage = PyObject_CallMethod(image, "copy", NULL);
    if ((core = (ImagingObject *)PyObject_GetAttrString(newimage, "im")) == NULL)
    {
        return NULL;
    } 
    imOut = core->image; 
    Py_DECREF(core);

    if (!PyArg_ParseTuple(empty_color, "iiii", &er, &eg, &eb, &ea))
    {
        return NULL;
    } 

    width = imIn->xsize;
    height = imIn->ysize;
    
    for (j = 0; j < height; j++)
    {
        for (i = 0; i < width; i++)
        {
            found = 0;
            rsum = 0;
            gsum = 0;
            bsum = 0; 
            asum = 0;

            pixel = imOut->image[j];
            pixel += i * 4;
            pixel[0] = er;
            pixel[1] = eg;
            pixel[2] = eb;
            pixel[3] = ea;

            for (ai = 0; ai < antialias; ai++)
            {
                xx = 2.0 * (i + ai / (double)antialias) / width - 1; 

                for (aj = 0; aj < antialias; aj++)
                {
                    yy = 2.0 * (j + aj / (double)antialias) / height - 1;

                    xnew = xx;
                    ynew = yy;

                    /* ----------- */
                    warp(func, xx, yy, &xnew, &ynew);

                    /* ------------------------- */

                    i2 = 0.5 * width * (xnew + 1);
                    j2 = 0.5 * height * (ynew + 1);
                    
                    i3 = round(i2);
                    j3 = round(j2);

                    if (i3 < 0 || i3 >= width || j3 < 0 || j3 >= height)
                    {
                        continue;
                    }

                    pixel = (UINT8*)imIn->image[j3];
                    pixel += i3 * 4;

                    rsum += pixel[0];
                    gsum += pixel[1];
                    bsum += pixel[2];
                    asum += pixel[3];
                    found++;
                }
            }

            if (found > 0)
            {
                pixel = imOut->image[j];
                pixel += i * 4;
                pixel[0] = rsum / found;
                pixel[1] = gsum / found;
                pixel[2] = bsum / found;
                pixel[3] = asum / found;
            }
        }
    }

    return (PyObject *)newimage;
}

static PyObject* lens_warp(PyObject *self, PyObject *args)
{
    PyObject *img = _lens_warp(self, args, _xy_warp);
    return img;
}

static PyObject* radian_warp(PyObject *self, PyObject *args)
{
    PyObject *img = _lens_warp(self, args, _radian_warp);
    return img;
}

/* 波浪效果 */
static PyObject* wave_warp(PyObject *self, PyObject *args)
{
    PyObject *image;
    PyObject *newimage;
    ImagingObject *core;
    Imaging imIn, imOut;
    int i, j, ai, aj; 
    int found, rsum, gsum, bsum, asum;
    int antialias = 2;
    double xx, yy;
    int width, height;
    double i2, j2;
    double xnew, ynew;
    UINT8 *pixel; 
    int i3, j3;
    PyObject *empty_color;
    double dw = 1, dh=0.3;
    double radian;
    double offset;
    int er, eg, eb, ea;
    double xoffset;

    if (!PyArg_ParseTuple(args, "OdddiO", &image, &dw, &dh, &xoffset, &antialias, &empty_color))
    {
        return NULL;
    } 

    if ((core = (ImagingObject *)PyObject_GetAttrString(image, "im")) == NULL)
    {
        return NULL;
    } 
    imIn = core->image;
    Py_DECREF(core);

    /* copy a new image */
    newimage = PyObject_CallMethod(image, "copy", NULL);
    if ((core = (ImagingObject *)PyObject_GetAttrString(newimage, "im")) == NULL)
    {
        return NULL;
    } 
    imOut = core->image; 
    Py_DECREF(core);

    if (!PyArg_ParseTuple(empty_color, "iiii", &er, &eg, &eb, &ea))
    {
        return NULL;
    } 

    width = imIn->xsize;
    height = imIn->ysize;
    
    for (j = 0; j < height; j++)
    {
        for (i = 0; i < width; i++)
        {
            found = 0;
            rsum = 0;
            gsum = 0;
            bsum = 0; 
            asum = 0;

            pixel = imOut->image[j];
            pixel += i * 4;
            pixel[0] = er;
            pixel[1] = eg;
            pixel[2] = eb;
            pixel[3] = ea;

            for (ai = 0; ai < antialias; ai++)
            {
                xx = i + ai / (double)antialias;

                for (aj = 0; aj < antialias; aj++)
                {
                    yy = j + aj / (double)antialias;

                    /* ------------------------- */
                    radian = 2 * 3.14159265 * (xx + xoffset) / (double)width * dw;
                    offset = 0.5 * sin(radian) * height * dh;

                    xnew = xx;
                    ynew = yy + offset; 
                    
                    /* ------------------------- */

                    i3 = round(xnew);
                    j3 = round(ynew);
                    /* printf("%d %d %d %d\n", i, j, i3, j3); */

                    if (i3 < 0 || i3 >= width || j3 < 0 || j3 >= height)
                    {
                        continue;
                    }

                    pixel = (UINT8*)imIn->image[j3];
                    pixel += i3 * 4;

                    rsum += pixel[0];
                    gsum += pixel[1];
                    bsum += pixel[2];
                    asum += pixel[3];
                    found++;
                }
            }

            if (found > 0)
            {
                pixel = imOut->image[j];
                pixel += i * 4;
                pixel[0] = rsum / found;
                pixel[1] = gsum / found;
                pixel[2] = bsum / found;
                pixel[3] = asum / found;
            }
        }
    }

    return (PyObject *)newimage;
}


static PyMethodDef CoreMethods[] = {
    {"lens_warp", lens_warp, METH_VARARGS, "Global warp"},
    {"radian_warp", radian_warp, METH_VARARGS, "Radian Warp"},
    {"wave_warp", wave_warp, METH_VARARGS, "Wave"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initEffectLabCore()
{
    Py_InitModule("EffectLabCore", CoreMethods);
}









