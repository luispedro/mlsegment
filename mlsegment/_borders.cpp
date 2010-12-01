#include "numpypp/array.hpp"
#include "numpypp/dispatch.hpp"
#include "utils.hpp"
#include "_filters.h"

extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}

namespace{

const char TypeErrorMsg[] =
    "Type not understood. "
    "This is caused by either a direct call to _borders (which is dangerous: types are not checked!) or a bug in borders.py.\n";


template<typename T>
bool borders(numpy::aligned_array<T> array, numpy::aligned_array<T> filter, numpy::aligned_array<bool> result, T i, T j) {
    gil_release nogil;
    const int N = array.size();
    typename numpy::aligned_array<T>::iterator iter = array.begin();
    filter_iterator<T> fiter(array.raw_array(), filter.raw_array(), EXTEND_CONSTANT, true);
    const int N2 = fiter.size();
    bool* out = result.data();
    bool any = false;

    for (int ii = 0; ii != N; ++ii, fiter.iterate_with(iter), ++iter, ++out) {
        const T cur = *iter;
        T other;
        if (cur == i) other = j;
        else if (cur == j) other = i;
        else continue;
        for (int j = 0; j != N2; ++j) {
            T val ;
            if (fiter.retrieve(iter, j, val) && (val == other)) {
                *out = true;
                any = true;
            }
        }
    }
    return any;
}
template<typename T>
void neighbours(numpy::aligned_array<T> array, numpy::aligned_array<T> filter, numpy::aligned_array<bool> result) {
    gil_release nogil;
    const int N = array.size();
    typename numpy::aligned_array<T>::iterator iter = array.begin();
    filter_iterator<T> fiter(array.raw_array(), filter.raw_array(), EXTEND_CONSTANT, true);
    const int N2 = fiter.size();

    for (int ii = 0; ii != N; ++ii, fiter.iterate_with(iter), ++iter) {
        const T cur = *iter;
        for (int j = 0; j != N2; ++j) {
            T val ;
            if (fiter.retrieve(iter, j, val) && (val != cur)) {
                result.at(val, cur) = true;
            }
        }
    }
}


PyObject* py_borders(PyObject* self, PyObject* args) {
    PyArrayObject* array;
    PyArrayObject* filter;
    PyArrayObject* output;
    int i;
    int j;
    int always_return;
    if (!PyArg_ParseTuple(args,"OOOiii", &array, &filter, &output, &i, &j, &always_return)) return NULL;
    if (!PyArray_Check(array) || !PyArray_Check(filter) || PyArray_TYPE(array) != PyArray_TYPE(filter) ||
        !PyArray_Check(output) || PyArray_TYPE(output) != NPY_BOOL || !PyArray_ISCARRAY(output)) {
        PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
        return NULL;
    }
    for (int d = 0; d != PyArray_NDIM(array); ++d) {
        if (PyArray_DIM(array, d) != PyArray_DIM(output, d)) {
            PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
            return NULL;
        }
    }
    Py_INCREF(output);

    bool has_any;
    switch(PyArray_TYPE(array)) {
#define HANDLE(type) \
        has_any = borders<type>( \
                    numpy::aligned_array<type>(array), \
                    numpy::aligned_array<type>(filter), \
                    numpy::aligned_array<bool>(output), \
                    static_cast<type>(i), \
                    static_cast<type>(j));
        HANDLE_TYPES();
#undef HANDLE
        default:
        PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
        return NULL;
    }
    if (always_return || has_any) return PyArray_Return(output);

    Py_DECREF(output);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* py_neighbours(PyObject* self, PyObject* args) {
    PyArrayObject* array;
    PyArrayObject* filter;
    PyArrayObject* output;
    if (!PyArg_ParseTuple(args,"OOO", &array, &filter, &output)) return NULL;
    if (!PyArray_Check(array) || !PyArray_Check(filter) || PyArray_TYPE(array) != PyArray_TYPE(filter) ||
        !PyArray_Check(output) || PyArray_TYPE(output) != NPY_BOOL || !PyArray_ISCARRAY(output)) {
        PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
        return NULL;
    }
    for (int d = 0; d != PyArray_NDIM(array); ++d) {
        //if (PyArray_DIM(array, d) != PyArray_DIM(output, d)) {
        //    PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
        //    return NULL;
        //}
    }
    Py_INCREF(output);

    switch(PyArray_TYPE(array)) {
#define HANDLE(type) \
        neighbours<type>( \
                    numpy::aligned_array<type>(array), \
                    numpy::aligned_array<type>(filter), \
                    numpy::aligned_array<bool>(output) \
                    );
        HANDLE_INTEGER_TYPES();
#undef HANDLE
        default:
        PyErr_SetString(PyExc_RuntimeError, TypeErrorMsg);
        return NULL;
    }
    return PyArray_Return(output);
}

PyMethodDef methods[] = {
  {"borders",(PyCFunction)py_borders, METH_VARARGS, NULL},
  {"neighbours",(PyCFunction)py_neighbours, METH_VARARGS, NULL},
  {NULL, NULL,0,NULL},
};

} // namespace
extern "C"
void init_borders()
  {
    import_array();
    (void)Py_InitModule("_borders", methods);
  }

