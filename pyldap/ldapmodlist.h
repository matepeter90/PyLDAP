/*
 * ldapmodlist.h
 *
 *  Created on: 7 Nov 2014
 *      Author: noirello
 */

#ifndef PYLDAP_LDAPMODLIST_H_
#define PYLDAP_LDAPMODLIST_H_

#include <Python.h>
#include "structmember.h"

//MS Windows
#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__)

#include <windows.h>
#include <winldap.h>

//Unix
#else
#include <ldap.h>

#endif

typedef struct {
	PyObject_HEAD
	LDAPMod **mod_list;
	unsigned short int last;
	unsigned short int size;
	PyObject *entry;
} LDAPModList;

extern PyTypeObject LDAPModListType;

LDAPModList *LDAPModList_New(PyObject *entry, unsigned short int size);
int LDAPModList_Add(LDAPModList *self, int mod_op, PyObject *key, PyObject *value);
PyObject *LDAPModList_Pop(LDAPModList *self);
int LDAPModList_Empty(LDAPModList *self);

#endif /* PYLDAP_LDAPMODLIST_H_ */
