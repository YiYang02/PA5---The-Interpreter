# Raymond Zhao (rfz5nt)
# Daniel Coo (djc4ku)

# Read in .cl-type file
# Separate into class_map, imp_map, parent_map, and ast
from __future__ import division
import sys, traceback, copy, re
# Need to increase recursion limit to detect stack overflow, Python's 
# default is kind of low.
sys.setrecursionlimit(10000)

# Exp object to handle easy expressions

class Exp:
	def __init__(self, loc=None, exp_kind=None, exp=None):
		self.loc = loc
		self.exp_kind = exp_kind
		self.exp = exp

	def __repr__(self):
		if self.exp_kind == "new":
			return "New(%s)" % (str(self.exp))
		elif self.exp_kind == "isvoid":
			return "IsVoid(%s)" % (str(self.exp))
		elif self.exp_kind == "if":
			return "If(%s)" % (str(self.exp))
		elif self.exp_kind == "block":
			return "Block(%s)" % (str(self.exp))
		elif self.exp_kind == "while":
			return "While(%s)" % (str(self.exp))
		elif self.exp_kind == "lt":
			return "Lt(%s)" % (str(self.exp))
		elif self.exp_kind == "le":
			return "Le(%s)" % (str(self.exp))
		elif self.exp_kind == "negate":
			return "Negate(%s)" % (str(self.exp))
		elif self.exp_kind == "eq":
			return "Eq(%s)" % (str(self.exp))
		elif self.exp_kind == "times":
			return "Times(%s)" % (str(self.exp))
		elif self.exp_kind == "divide":
			return "Divide(%s)" % (str(self.exp))
		elif self.exp_kind == "minus":
			return "Minus(%s)" % (str(self.exp))
		elif self.exp_kind == "plus":
			return "Plus(%s)" % (str(self.exp))
		elif self.exp_kind == "not":
			return "Not(%s)" % (str(self.exp))
		elif self.exp_kind == "integer":
			return "Integer(%s)" % (str(self.exp))
		elif self.exp_kind == "string":
			return "String(%s)" % (str(self.exp))
		elif self.exp_kind == "true":
			return "Bool(%s)" % (str(self.exp))
		elif self.exp_kind == "false":
			return "Bool(%s)" % (str(self.exp))
		elif self.exp_kind == "identifier":
			return "ID(%s)" % (str(self.exp))
		else:
			return "exp not handled in to string"

#Internal handles internal methods such as copy, in_int, substr, etc.

class Internal(Exp):
	def __init__(self, loc=None,parent_class=None,return_type=None,exp=None):
		Exp.__init__(self, loc, "internal",exp)
		self.return_type = return_type	
		self.parent_class = parent_class
		
	def __repr__(self):
		return "Internal(%s,%s,%s)" % (self.parent_class,self.exp, self.return_type)

#Some expressions require a lot more to work with compared to what the
#Exp object has to offer

class Assign(Exp):
	def __init__(self, loc=None, var=None, exp=None):
		Exp.__init__(self,loc,"assign",exp)
		self.var = var
	def __repr__(self):
		return "Assign(%s,%s)" % (self.var,self.exp)

class Self_Dispatch(Exp):
	def __init__(self, loc=None, fname=None, exp=None):
		Exp.__init__(self,loc,"self_dispatch",exp) 
		self.fname = fname
	def __repr__(self):
		return "Self_Dispatch(%s,%s)" % (self.fname,self.exp)

class Dynamic_Dispatch(Exp):
	def __init__(self, loc=None, e=None, fname=None, exp=None):
		Exp.__init__(self,loc,"dynamic_dispatch",exp) 
		self.e = e
		self.fname = fname
	def __repr__(self):
		return "Dynamic_Dispatch(%s,%s,%s)" % (self.e,self.fname,self.exp)

class Static_Dispatch(Exp):
	def __init__(self, loc=None, e=None, static_type=None, fname=None, exp=None):
		Exp.__init__(self,loc,"static_dispatch",exp)
		self.e = e
		self.static_type = static_type
		self.fname = fname
	def __repr__(self):
		return "Static_Dispatch(%s,%s,%s,%s)" % (self.e,self.static_type,self.fname,self.exp)

class Case(Exp):
	def __init__(self,loc=None,exp=None,case_element_list=None):
		Exp.__init__(self,loc,"case",exp)
		self.case_element_list = case_element_list
	def __repr__(self):
		return "Case(%s,%s)" % (self.exp,self.case_element_list)

class Case_Element():
	def __init__(self,variable=None,type_name=None,body=None):
		self.variable = variable
		self.type_name = type_name
		self.body = body
	def __repr__(self):
		return "Case_Element(%s,%s,%s)" % (self.variable,self.type_name,self.body)

class Let(Exp):
	def __init__(self,loc=None,binding_list=None,exp=None):
		Exp.__init__(self,loc,"let",exp)
		self.binding_list = binding_list
	def __repr__(self):
		return "Let(%s,%s)" % (self.binding_list, self.exp)

class Let_Binding():
	def __init__(self,variable=None,binding_type=None,value=None):
		self.variable = variable
		self.binding_type = binding_type
		self.value = value
	def __repr__(self):
		return "Binding(%s,%s,%s)" % (self.variable,self.binding_type,self.value)

#Types of CoolObjects: Ints, Bools, Strings, and the general object
		
class CoolObject:
	def __init__(self, cname=None, attr_and_locs={}, loc=0):
		self.cname = cname
		self.attr_and_locs = attr_and_locs
		self.loc = loc
	def __repr__(self):
		return "CoolObject(%s,%s,loc=%s)" % (self.cname,self.attr_and_locs,self.loc)

class CoolInt(CoolObject):
	def __init__(self, value=0):
		CoolObject.__init__(self,"Int", {},0)
		self.value = value
	def __repr__(self):
		return "CoolInt(%s,loc=%s)" % (self.value,self.loc)

class CoolString(CoolObject):
	def __init__(self, value="", length=0):
		CoolObject.__init__(self,"String",{},0)
		self.value = value
		self.length = length
	def __repr__(self):
		return "CoolString(%s,%s,loc=%s)" % (self.value,self.length,self.loc)

class CoolBool(CoolObject):
	def __init__(self, value="false"):
		CoolObject.__init__(self,"Bool",{},0)
		self.value = value
	def __repr__(self):
		return "CoolBool(%s,loc=%s)" % (self.value,self.loc)

class Void():
	def __init__(self, value=None):
		self.cname = "Void"
		self.value = value
	def __repr__(self):
		return "Void"

# Helper functions
def print_list(a):
	for elt in a:
		print(elt)

def is_int(n):
	try:
		int(n)
		return True
	except ValueError:
		return False

# Finds the minimum value of a dictionary
# (k,v)
# IMPORTANT: types cannot be bound twice in a case statement, so all the
# types in the case elements list are unique
def find_min(d):
	current_key_min = ""
	current_min = sys.maxint	
	for k,v in d.items():
		if v < current_min:
			current_key_min = k
			current_min = v
	return (current_key_min)

# Returns ancestory list of class a based on pmap
# e.g. a=IO  return: [IO, Object]
def get_inhr_list(a, ancestors, e):
	if a == "Object":
		ancestors.append(a)
		return ancestors
	else:
		if a not in pmap:
			msg = "ERROR: %s: Exception: case on void" % (e.loc)
			sys.exit(msg)
		ancestors.append(a)
		return get_inhr_list(pmap[a], ancestors, e)

# Returns the least common ancestor between class=a and class=b
def lub(a, b):
	ancestors_a = get_inhr_list(a, [], None)
	ancestors_b = get_inhr_list(b, [], None)
	for c in ancestors_a:
		for c2 in ancestors_b:
			if c == c2:
				return c
	return None

# Debugging and Tracing

do_debug = False
global indent_count
indent_count = 0
def debug_indent():
	global indent_count
	if do_debug:
		for i in range(indent_count):
			print(" ")

def debug(e):
	if do_debug:
		print("%s" % (e))

def print_map(hmap):
	for k in hmap:
		for v in hmap[k]:
			print("%s -> %s" % (k, v))
		print

def print_pmap(pm):
	for k in pm:
		print("%s -> %s" % (k, pm[k]))

fname = sys.argv[1]

# Read in .cl-type file
type_file = []
with open(fname, 'r') as fin:
	for line in fin:
		type_file.append(line.rstrip('\n'))

io_cmap = []
io_imap = []
io_pmap = []
io_ast  = []

in_cmap = True
in_imap = False
in_pmap = False

for line in type_file:
	if line == "implementation_map":
		in_cmap = False
		in_imap = True
	elif line == "parent_map":
		in_imap = False
		in_pmap = True
	
	if in_cmap:
		io_cmap.append(line)
	elif in_imap:
		io_imap.append(line)
	elif in_pmap:
		io_pmap.append(line)


# Separate ast from pmap
# Start of ast will always be the second integer
int_count = 0
split_pos = 0
for inx, line in enumerate(io_pmap):
	if is_int(line):
		int_count += 1  
	if int_count > 1:
		split_pos = inx
		break

io_ast = io_pmap[split_pos:]
io_pmap = io_pmap[0:split_pos]

# Deerialize the class_map
class_map = {}
imp_map = {}
pmap = {}
# li : remaining part of class-map
# helper : function

# All reading in expressions

def read_id(e):
	idloc = e.pop(0)
	idname = e.pop(0)
	t = Exp(idloc, "identifier", idname)
	return t

def read_internal_exp(e):
	loc = e.pop(0)  # loc is always 0
	ret_type = e.pop(0)
	internal = e.pop(0)
	exp_body = e.pop(0)	# e.g. Object.abort  IO.in_int. See PA4 AST third bullet
	parent_class = exp_body.split(".")[0]
	t = Internal(loc,parent_class,ret_type,exp_body)
	return t

def read_case_element(e):
	variable = read_id(e)
	type_name = read_id(e)
	body = read_exp(e)
	t = Case_Element(variable,type_name,body)
	return t

def read_binding(e):
	binding_kind = e.pop(0)
	if binding_kind == "let_binding_init":
		variable = read_id(e)
		binding_type = read_id(e)
		body = read_exp(e)
		t = Let_Binding(variable,binding_type,body)
		return t
	elif binding_kind == "let_binding_no_init":
		variable = read_id(e)
		binding_type = read_id(e)
		body = None
		t = Let_Binding(variable,binding_type,body)
		return t
	else:
		print("Binding type does not exist")
		return None

def read_exp(e):
    # Know that we need to read an exp
    # return a tuple (loc, exp_kind, exp subparts)
    # recurse on the subparts

    # Test if annotated expression. Types are always capitalized
    print("exp is ", e)
    if e[1][0].isupper():
        loc = e.pop(0)
        exp_type = e.pop(0)
        exp_kind = e.pop(0)
    else:	
        loc = e.pop(0)
        exp_kind = e.pop(0)

    # Read expressions based on exp_kind
    if exp_kind == "assign":
        var = read_id(e)
        body = read_exp(e)
        t = Assign(loc,var.exp,body)
        return t
    elif exp_kind == "new":
        id_ver = read_id(e) 
        t = Exp(id_ver.loc, exp_kind, id_ver.exp)
        return t
    elif exp_kind == "self_dispatch":
        funcid = read_id(e)
        fname = funcid.exp
        num_of_args = int(e.pop(0))
        arg_list = [read_exp(e) for i in range(num_of_args)]
        t = Self_Dispatch(loc, fname, arg_list)
        return t
    elif exp_kind == "dynamic_dispatch":
        e0 = read_exp(e)
        funcid = read_id(e)
        fname = funcid.exp
        num_of_args = int(e.pop(0))
        arg_list = [read_exp(e) for i in range(num_of_args)]
        t = Dynamic_Dispatch(loc, e0, fname, arg_list)
        return t
    elif exp_kind == "static_dispatch":
        e0 = read_exp(e)	
        static_type = read_id(e)
        funcid = read_id(e)
        num_of_args = int(e.pop(0))
        arg_list = [read_exp(e) for i in range(num_of_args)]
        t = Static_Dispatch(loc, e0, static_type.exp, funcid.exp, arg_list)
        return t
    elif exp_kind == "let":
        num_of_bindings = int(e.pop(0))
        binding_list = [read_binding(e) for i in range(num_of_bindings)]
        body = read_exp(e)
        t = Let(loc,binding_list,body)
        return t
    elif exp_kind == "case":
        case_exp = read_exp(e)
        num_of_elements = int(e.pop(0))
        case_element_list = [read_case_element(e) for i in range(num_of_elements)]
        t = Case(loc,case_exp,case_element_list)
        return t
    elif exp_kind == "if":
        predicate = read_exp(e)
        then_statement = read_exp(e)
        else_statement = read_exp(e)
        t = Exp(loc, exp_kind, [predicate,then_statement,else_statement])
        return t
    elif exp_kind == "block":
        num_of_exps = int(e.pop(0))	
        exp_list = [read_exp(e) for i in range(num_of_exps)]
        t = Exp(loc, exp_kind, exp_list)
        return t
    elif exp_kind == "while":
        predicate = read_exp(e)
        body = read_exp(e)
        t = Exp(loc, exp_kind, [predicate,body])
        return t
    elif exp_kind == "isvoid":
        t = Exp(loc, exp_kind, read_exp(e)) 
        return t
    elif exp_kind == "negate":
        t = Exp(loc, exp_kind, read_exp(e))
        return t
    elif exp_kind in ["plus", "minus", "times", "divide", "lt", "le", "eq"]:
        first_exp = read_exp(e)
        second_exp = read_exp(e)
        t = Exp(loc, exp_kind, [first_exp, second_exp])
        return t
    elif exp_kind == "not":
        t = Exp(loc, exp_kind, read_exp(e))
        return t
    elif exp_kind == "integer":
        int_constant = e.pop(0)
        t = Exp(loc, exp_kind, int_constant)
        return t
    elif exp_kind == "string":
        str_constant = e.pop(0) 
        t = Exp(loc, exp_kind, str_constant)
        return t
    elif exp_kind == "true":
        t = Exp(loc, exp_kind, "true")
        return t
    elif exp_kind == "false":
        t = Exp(loc, exp_kind, "false")
        return t
    elif exp_kind == "identifier":
        return read_id(e)		
    else:
        print("Expression %s not handled in read_exp(e)" % (exp_kind))
        sys.exit(0)
	

def read_cmap(cmap_list):
	num_classes = int(cmap_list.pop(0))
	while num_classes > 0:
		try:
			attrs = []
			cname = cmap_list.pop(0)
			#print cname
			num_attrs = int(cmap_list.pop(0))
			#print num_attrs
			while num_attrs > 0:
				initialize = cmap_list.pop(0)
				#print initialize
				attr_name = cmap_list.pop(0)
				#print attr_name
				attr_type = cmap_list.pop(0)
				#print attr_type
				attr_exp = []
				if initialize == "initializer":
					attr_exp.append(read_exp(cmap_list))
				attrs.append((attr_name, attr_type, attr_exp))  
				num_attrs -= 1
			num_classes -= 1
			class_map[cname] = attrs
		except ValueError:
			print("ValueError, messed up somewhere in read_cmap")
			sys.exit(0)

# key: (class name, method name) value: (formals list, method body)
def read_impmap(imap):
	num_classes = int(imap.pop(0))
	while num_classes > 0:
		try:
			class_name = imap.pop(0)
			num_of_methods = int(imap.pop(0))
			for i in range(num_of_methods):
				method_name = imap.pop(0)
				num_of_formals = int(imap.pop(0))
				formal_list = [imap.pop(0) for i in range(num_of_formals)]	
				parent_class = imap.pop(0)
				
				# Check if internal method
				# Contents of imap if internal
				# 0				imap[0]
				# Object		imap[1]
				# internal		imap[2]
				# Object.abort	imap[3]
				if imap[2] == "internal":
					body_exp = read_internal_exp(imap)
				else:
					body_exp = read_exp(imap)

				imp_map[(class_name,method_name)] = (formal_list,body_exp)
			num_classes -= 1
		except ValueError as e:
			print("ValueError, messed up while reading the lines from imp map")
			print(e)
			sys.exit(0)

#Reading the parent map to get all the inheritance information for
#case and the lowest common ancestor algorithm

def read_pmap(pmap_list):
	num_classes = int(pmap_list.pop(0))
	while num_classes > 0:
		c = pmap_list.pop(0)
		d = pmap_list.pop(0)
		pmap[c] = d
		num_classes -= 1

read_cmap(io_cmap[1:])
read_impmap(io_imap[1:])
read_pmap(io_pmap[1:])

do_print = False
if do_print:
	print("CLASS_MAP")
	print_map(class_map)
	print("IMP_MAP")
	print_map(imp_map)
	print("PARENT_MAP")
	print_pmap(pmap)

new_location_counter = 1000

#newloc should create a location for the store that is unique

def newloc():
	global new_location_counter
	new_location_counter += 1	
	return new_location_counter

#default_value means D_t, assigns a default value dependent on type tag

def default_value(typename):
	if typename == "Int":
		return CoolInt(0)
	elif typename == "String":
		return CoolString("",0)
	elif typename == "Bool":
		return CoolBool("false")
	else:
		return Void()

# Parameters:
# 	so		: self object
# 	store 	: store maps addresses to values
#	env		: environment maps variables to addresses
#	e		: the expression to evaluate
#
# Return Value:
#	(new_value, updated_store)

global activation_record
activation_record = 0

def eval(self_object,store,environment,exp):
	global activation_record
	global indent_count
	indent_count += 2
	debug_indent() ; debug("eval: %s" % (exp))
	debug_indent() ; debug("so    = %s" % (self_object))
	debug_indent() ; debug("store = %s" % (store))
	debug_indent() ; debug("env   = %s" % (environment))
	debug_indent() ; debug("exp = %s" % (exp))
	debug_indent() ; debug("exp_kind   = %s" % (exp.exp_kind))

	if exp.exp_kind == "assign":
		debug("\nIN ASSIGN\n")
		(v1,s2) = eval(self_object,store,environment,exp.exp)	
		l1 = environment[exp.var]	
		del s2[l1]
		s3 = s2
		s3[l1] = v1
		v1.loc = l1
		debug_indent() ; debug("ret = %s" % (v1))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (v1,s3)

	elif exp.exp_kind == "new":
		if activation_record > 999:
			sys.exit("ERROR: %s: newException: stack overflow" % (exp.loc))
		activation_record += 1;
		debug("\nIN NEW\n")
		t0 = exp.exp
		if t0 == "SELF_TYPE":
			t0 = self_object.cname
		else:
			t0 = exp.exp
		attrs_and_inits = class_map[t0]
		new_attrs_locs = [newloc() for x in attrs_and_inits]
		attr_names = [attr_name for (attr_name,attr_type,attr_exp) in attrs_and_inits]
		attrs_and_locs = dict(zip(attr_names, new_attrs_locs))
		if t0 in ["String", "Int","Bool"]:
			v1 = default_value(t0)
			v1.attr_and_locs = attrs_and_locs
		else:
			v1 = CoolObject(t0, attrs_and_locs)
		# iterate through key,value pairs (attrname to loc)
		s2 = copy.deepcopy(store)
		for (attr_name, attr_loc) in attrs_and_locs.items():
		# find the attr_name in the class map
			for (attr_name2, attr_type, attr_exp) in attrs_and_inits:
		# get the type from it and return the default value, make the pairing
				if attr_name == attr_name2:
					s2[attr_loc] = default_value(attr_type)
					s2[attr_loc].loc = attr_loc
		final_store = copy.deepcopy(s2)
		for (attr_name,_,attr_init) in attrs_and_inits:
			if attr_init != []:
				(_,current_store) = eval(v1,final_store,attrs_and_locs,Assign(0,attr_name,attr_init[0]))
				final_store = copy.deepcopy(current_store)
		debug_indent() ; debug("ret = %s" % (v1))
		debug_indent() ; debug("rets = %s" % (final_store))
		indent_count -= 2
		activation_record -= 1;
		return (v1,final_store)

	elif exp.exp_kind == "self_dispatch":
		if activation_record > 999:
			sys.exit("ERROR: %s: selfException: stack overflow" % (exp.loc))
		debug("\nIN SELF_DISPATCH\n")
		# call dynamic_dispatch, but use the self object for the receiver exp
		self_exp = Exp(0,"identifier","self")
		ret_exp = Dynamic_Dispatch(exp.loc,self_exp,exp.fname,exp.exp)
		(ret_value,ret_store) = eval(self_object,store,environment,ret_exp)
		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (ret_store))
		indent_count -= 2
		return (ret_value,ret_store)

	elif exp.exp_kind == "dynamic_dispatch":
		if activation_record > 999:
			sys.exit("ERROR: %s: dynamicException: stack overflow" % (exp.loc))
		activation_record += 1
		debug("\nIN DYNAMIC_DISPATCH\n")
		current_store = store
		arg_values = []
		# evaluate each argument and update store
		for arg in exp.exp:
			(arg_value, new_store) = eval(self_object,current_store,environment,arg)
			current_store = new_store
			arg_values.append(arg_value)

		# evaluate receiver object
		(v0,s_nplus2) = eval(self_object,current_store,environment,exp.e)
		# look into imp_map
		if (v0.cname,exp.fname) not in imp_map:
			msg = "ERROR: %s: Exception: dispatch on void" % (exp.loc)
			sys.exit(msg)
		(formals,body) = imp_map[(v0.cname,exp.fname)]
		# make new locations for each of the formals found in imp_map
		new_arg_locs = [ newloc() for x in formals]

		# make an updated store and add new locs to arg values
		s_nplus3 = s_nplus2
		store_update = dict(zip(new_arg_locs, arg_values))
		for (l,value) in store_update.items():
			value.loc = l
			s_nplus3[l] = value

		# need to have v0.attr_and_locs and imp_map formals to their locations in the new_env
		# and they shadow the attributes

		new_environment = copy.deepcopy(v0.attr_and_locs)

		environment_update = dict(zip(formals,new_arg_locs))
		for (identifier,loc) in environment_update.items():
			new_environment[identifier] = loc

		(ret_value,ret_store) = eval(v0,s_nplus3,new_environment,body)
		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (ret_store))
		indent_count -= 2
		activation_record -= 1;
		return (ret_value,ret_store)

	elif exp.exp_kind == "static_dispatch":
		if activation_record > 999:
			sys.exit("ERROR: %s: staticException: stack overflow" % (exp.loc))
		activation_record += 1
		debug("\nIN STATIC_DISPATCH\n")
		current_store = store
		arg_values = []
		for arg in exp.exp:
			(arg_value, new_store) = eval(self_object,current_store,environment,arg)
			current_store = new_store
			arg_values.append(arg_value)
		(v0,s_nplus2) = eval(self_object,current_store,environment,exp.e)
		# Only change within static_dispatch
		# v0.cname -> exp.static_type
		if (v0.cname,exp.fname) not in imp_map:
			msg = "ERROR: %s: Exception: static dispatch on void" % (exp.loc)
			sys.exit(msg)
		(formals,body) = imp_map[(exp.static_type,exp.fname)]
		new_arg_locs = [ newloc() for x in formals]
		s_nplus3 = s_nplus2
		store_update = dict(zip(new_arg_locs, arg_values))
		for (l,value) in store_update.items():
			value.loc = l
			s_nplus3[l] = value
		new_environment = v0.attr_and_locs
		environment_update = dict(zip(formals,new_arg_locs))
		for (identifier,loc) in environment_update.items():
			new_environment[identifier] = loc
		(ret_value,ret_store) = eval(v0,s_nplus3,new_environment,body)
		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (ret_store))
		indent_count -= 2
		activation_record -= 1;
		return (ret_value,ret_store)

	elif exp.exp_kind == "if":
		debug("\nIN IF\n")
		# eval the first expression and go off there (true or false)
		e1 = exp.exp[0]
		cool_bool,s2 = eval(self_object,store,environment,e1)
		# If-True
		if cool_bool.value == "true":
			e2 = exp.exp[1]	
			ret_value,ret_store = eval(self_object,s2,environment,e2)
			debug_indent() ; debug("ret = %s" % (ret_value))
			debug_indent() ; debug("rets = %s" % (ret_store))
			indent_count -= 2
			return ret_value,ret_store
		# If-False
		elif cool_bool.value == "false":
			e3 = exp.exp[2]
			ret_value,ret_store = eval(self_object,s2,environment,e3)	
			debug_indent() ; debug("ret = %s" % (ret_value))
			debug_indent() ; debug("rets = %s" % (ret_store))
			indent_count -= 2
			return ret_value,ret_store
		# This cannot happen
		else:
			print("Problem with if")
			sys.exit(0)
			return None
	
	elif exp.exp_kind == "block":
		debug("\nIN BLOCK\n")
		current_store = store #S1
		current_value = None
		for exp in exp.exp:
			ret_value,ret_store = eval(self_object,current_store,environment,exp)
			current_store = ret_store
			current_value = ret_value
		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (ret_store))
		indent_count -= 2
		return (ret_value,ret_store)
	
	elif exp.exp_kind == "let":
		debug("\nIN LET\n")
		if len(exp.binding_list) == 1:
			let_exp = exp.binding_list[0]
			e1 = let_exp.value
			v1 = None
			s2 = None
			if e1 == None:
				v1 = default_value(let_exp.binding_type.exp)
				s2 = store
			else:
				v1,s2 = eval(self_object,store,environment,e1)
			l1 = newloc()
			v1.loc = l1
			s3 = s2
			s3[l1] = v1
			env_id = let_exp.variable.exp
			e_prime = copy.deepcopy(environment)
			e_prime[env_id] = l1
			e2 = exp.exp
			v2,s4 = eval(self_object,s3,e_prime,e2)
			debug_indent() ; debug("ret = %s" % (v2))
			debug_indent() ; debug("rets = %s" % (s4))
			indent_count -= 2
			return v2,s4
		else:
			let_exp = exp.binding_list[0]
			e1 = let_exp.value
			v1 = None
			s2 = None
			if e1 is None:
				v1 = default_value(let_exp.binding_type.exp)
				s2 = store
			else:
				v1,s2 = eval(self_object,store,environment,e1)
			l1 = newloc()
			v1.loc = l1
			s3 = s2
			s3[l1] = v1
			env_id = let_exp.variable.exp
			e_prime = copy.deepcopy(environment)
			e_prime[env_id] = l1
			# need do another statement that will run into base case
			# get rid of first element of binding list
			exp.binding_list.pop(0)
			# Make a new let expression with new binding_list
			e2 = Let(exp.loc,exp.binding_list,exp.exp)
			v2,s4 = eval(self_object,s3,e_prime,e2)
			debug_indent() ; debug("ret = %s" % (v2))
			debug_indent() ; debug("rets = %s" % (s4))
			indent_count -= 2
			return v2,s4
	
	elif exp.exp_kind == "case":
		debug("\nIN CASE\n")
		e0 = exp.exp
		v0,s2 = eval(self_object,store,environment,e0)

		# Find lease common ancestor between case exp 
		# and case element list

		distances = {}
		case_types = [x.type_name.exp for x in exp.case_element_list]
		case_exp_inhr_list = get_inhr_list(v0.cname, [], e0)	
		count = 0
		found = False
		for i in case_exp_inhr_list:
			for j in case_types:
				if i == j:
					distances[j] = count
					found = True
			count += 1
		if not found:
			msg = "ERROR: %s: Exception: case without matching branch: %s" % (e0.loc, e0)
			sys.exit(msg)
		t_i = find_min(distances)

		l0 = newloc()
		s3 = s2
		v0.loc = l0
		s3[l0] = v0
		id_i = None
		e_i = None
		for case_element in exp.case_element_list:
			if case_element.type_name.exp == t_i:
				id_i = case_element.variable.exp
				e_i = case_element.body
		environment_prime = copy.deepcopy(environment)
		environment_prime[id_i] = l0
		v1,s4 = eval(self_object,s3,environment_prime,e_i)
		debug_indent() ; debug("ret = %s" % (v1))
		debug_indent() ; debug("rets = %s" % (s4))
		indent_count -= 2
		return v1,s4


	elif exp.exp_kind == "while":
		debug("\nIN WHILE\n")
		# exp.exp = [e1,e2]
		e1 = exp.exp[0]
		v1,s2 = eval(self_object,store,environment,e1)
		if v1.value == "true":
			e2 = exp.exp[1]
			v2,s3 = eval(self_object,s2,environment,e2)
			while_call = Exp(exp.loc,exp.exp_kind,[e1,e2])
			debug_indent() ; debug("ret = %s" % (while_call))
			debug_indent() ; debug("rets = %s" % (s3))
			indent_count -= 2
			return eval(self_object,s3,environment,while_call)
		elif v1.value == "false":	
			ret_val = Void()
			debug_indent() ; debug("ret = %s" % (ret_val))
			debug_indent() ; debug("rets = %s" % (s2))
			indent_count -= 2
			return ret_val,s2	
		else:
			print("this cannot happen with while")
			sys.exit(0)

	elif exp.exp_kind == "isvoid":
		debug("\nIN ISVOID\n")
		e1 = exp.exp
		v1,s2 = eval(self_object,store,environment,e1) 
		if isinstance(v1,Void):
			ret_val = CoolBool("true")
			debug_indent() ; debug("ret = %s" % (ret_val))
			debug_indent() ; debug("rets = %s" % (s2))
			indent_count -= 2
			return ret_val,s2 
		else:
			ret_val = CoolBool("false")
			debug_indent() ; debug("ret = %s" % (ret_val))
			debug_indent() ; debug("rets = %s" % (s2))
			indent_count -= 2
			return ret_val,s2

	elif exp.exp_kind == "negate":
		debug("\nIN NEGATE\n")
		e1 = exp.exp
		v1,s2 = eval(self_object,store,environment,e1)
		new_value = v1.value * -1
		if new_value < -2147483648:
			new_value += 2147483648
			new_value += 2147483648
		elif new_value > 2147483647:
			new_value -= 2147483648
			new_value += -2147483648
		debug_indent() ; debug("ret = %s" % (new_value))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (CoolInt(new_value),s2)

	elif exp.exp_kind == "plus":
		debug("\nIN PLUS\n")
		# Get each integer from plus expression
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,environment,e1)
		v2, s3 = eval(self_object,store,environment,e2)
		new_value = v1.value + v2.value
		# Handle wrap-around
		if new_value > 2147483647:
			new_value -= 2147483648
			new_value += -2147483648
		elif new_value < -2147483648:
			new_value += 2147483648
			new_value += 2147483648
		debug_indent() ; debug("ret = %s" % (new_value))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (CoolInt(new_value), s3)

	elif exp.exp_kind == "minus":
		debug("\nIN MINUS\n")
		# Get each integer from plus expression
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,environment,e1)
		v2, s3 = eval(self_object,store,environment,e2)
		new_value = v1.value - v2.value
		# Handle wrap-around
		if new_value < -2147483648:
			new_value += 2147483648
			new_value += 2147483648
		elif new_value > 2147483647:
			new_value -= 2147483648
			new_value += -2147483648
		debug_indent() ; debug("ret = %s" % (new_value))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (CoolInt(new_value), s3)

	elif exp.exp_kind == "times":
		debug("\nIN TIMES\n")
		# Get each integer from plus expression
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,environment,e1)
		v2, s3 = eval(self_object,store,environment,e2)
		new_value = v1.value * v2.value
		if new_value > 2147483647:
			new_value -= 2147483648
			new_value += -2147483648
		elif new_value < -2147483648:
			new_value += 2147483648
			new_value += 2147483648
		debug_indent() ; debug("ret = %s" % (new_value))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (CoolInt(new_value), s3)

	elif exp.exp_kind == "divide":
		debug("\nIN DIVIDE\n")
		# Get each integer from plus expression
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,environment,e1)
		v2, s3 = eval(self_object,store,environment,e2)
		if v2.value == 0:
			msg = "ERROR: %s: Exception: division by zero" % (e1.loc)
			sys.exit(msg)
		new_value = v1.value / v2.value
		if new_value > 2147483647:
			new_value -= 2147483648
			new_value += -2147483648
		elif new_value < -2147483648:
			new_value += 2147483648
			new_value += 2147483648
		debug_indent() ; debug("ret = %s" % (new_value))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (CoolInt(int(new_value)), s3)

	elif exp.exp_kind in ["lt","le","eq"]:
		debug("\nIN LT LE EQ\n")
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,environment,e1)
		v2, s3 = eval(self_object,store,environment,e2)
		ret_value = "";
		if exp.exp_kind == "lt":
			if v1.value < v2.value:
				ret_value = "true"
			else:
				ret_value = "false"
		elif exp.exp_kind == "le":
			if v1.value < v2.value or v1.value == v2.value:
				ret_value = "true"
			else:
				ret_value = "false"
		elif exp.exp_kind == "eq":
			if v1.cname in ["String","Int","Bool","Void"]:
			# TODO : Locations are not being set for CoolObjects
				if v1.value == v2.value:
					ret_value = "true"
				else:
					ret_value = "false"
			else:
				if v1.loc == v2.loc:
					ret_value = "true"
				else:
					ret_value = "false"
		else:
			print("Error: this shouldn't happen in compare")
			sys.exit(0)

		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (s3))
		indent_count -= 2
		return (CoolBool(ret_value), s3)

	elif exp.exp_kind == "not":
		debug("\nIN NOT\n")
		e1 = exp.exp
		v1, s2 = eval(self_object,store,environment,e1);
		ret_value = ""
		if v1.value == "true":
			ret_value = "false"
		else:
			ret_value = "true"
		debug_indent() ; debug("ret = %s" % (ret_value))
		debug_indent() ; debug("rets = %s" % (s2))
		indent_count -= 2
		return (CoolBool(ret_value), s2)	

	elif exp.exp_kind == "integer":
		debug("\nIN INTEGER\n")
		value = int(exp.exp)
		debug_indent() ; debug("ret = %s" % (value))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (CoolInt(value), store)

	elif exp.exp_kind == "string":
		debug("\nIN STRING\n")
		value = str(exp.exp)
		length = len(value)
		debug_indent() ; debug("ret = %s" % (value))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (CoolString(value,length), store)

	elif exp.exp_kind == "true":
		debug("\nIN TRUE\n")
		debug_indent() ; debug("ret = %s" % ("true"))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (CoolBool("true"),store)

	elif exp.exp_kind == "false":
		debug("\nIN FALSE\n")
		debug_indent() ; debug("ret = %s" % ("false"))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (CoolBool("false"),store)

	elif exp.exp_kind == "identifier":
		debug("\nIN IDENTIFIER\n")
		iden = exp.exp
		if iden == "self":
			debug_indent() ; debug("ret = %s" % (self_object))
			debug_indent() ; debug("rets = %s" % (store))
			indent_count -= 2
			return (self_object,store)
		l = environment[iden]
		value = store[l]
		debug_indent() ; debug("ret = %s" % (value))
		debug_indent() ; debug("rets = %s" % (store))
		indent_count -= 2
		return (value,store)
	
	elif exp.exp_kind == "internal":
		debug("\nIN INTERNAL\n")
		fname = exp.exp.split(".")[1]
		if fname == "out_string":
			string = store[environment['x']].value.replace("\\n","\n").replace("\\t","\t")
			if string != '\x00':
				sys.stdout.write(string)
				return self_object,store
			else:
				sys.stdout.write("")
				return self_object,store
		elif fname == "out_int":
			sys.stdout.write(str(store[environment['x']].value))
			return self_object,store
		elif fname == "in_string":
			try:
				read_line = raw_input()
				for c in read_line:
					if chr(ord(c)) == '\x00':
						return CoolString("",0),store
				return CoolString(read_line,0),store
			except EOFError:
				return CoolString("",0),store
		elif fname == "in_int":
			try:
				read_line = raw_input()
				# removing leading and trailing whitespace
				read_line = read_line.strip()

				# find all numbers in the string
				numbers = re.match(r'[-+]?\d+', read_line)
				if numbers != None:
					num = numbers.group()
					if int(num) > 2147483647 or int(num) < -2147483648:
						return CoolInt(0),store
					return CoolInt(int(num)),store
				else:
					return CoolInt(0),store
			except EOFError:
				return CoolInt(0),store
		elif fname == "length":
			return CoolInt(self_object.length),store
		elif fname == "concat":
			string1 = self_object.value.replace("\\n","\n")
			string2 = store[environment['s']].value.replace("\\n","\n")
			concat_str = string1 + string2
			return CoolString(concat_str,len(concat_str)),store
		elif fname == "substr":
			string = self_object.value.replace("\\n","\n")
			beg = int(store[environment['i']].value)
			length = int(store[environment['l']].value)
			if ((beg + length) > len(string)):
				msg = "ERROR: 0: Exception: String.substr out of range"
				sys.exit(msg)
			substring = string[beg:beg+length]
			return CoolString(substring,len(substring)),store
		elif fname == "abort":
			print("abort")
			sys.exit(0)	
		elif fname == "type_name":
			return_str = self_object.cname
			return CoolString(return_str,len(return_str)),store
		elif fname == "copy":
			# get the attributes and make new locations for them

			attr_list = list(self_object.attr_and_locs.keys())
			loc_list = list(self_object.attr_and_locs.values())
			new_locs = [ newloc() for i in attr_list ]

			## get the values from the self object and then putting 
			## into the store with the new locations

			values = [ store[i] for i in loc_list ]
			store_update = dict(zip(new_locs,values))
			s2 = store
			for (l,value) in store_update.items():
				value.loc = l
				s2[l] = value

			## return a new object with the old attributes to the
			## new locations

			new_attr_and_locs = dict(zip(attr_list,new_locs))
			shallow_copy = CoolObject(self_object.cname,new_attr_and_locs,newloc())
			return shallow_copy,s2
		else:
			print("Where did this internal come from?")
			sys.exit(0)
	
	else:
		print("Expression %s not handled" % (exp.exp_kind))
		sys.exit(0)

# ----------MAIN----------
	
# Environment, Store, and Values
# Environment is a list of tuples
# e.g. x lives at address 33 and y lives address 7
# [ ('x', 33), ('y', 7) ]
env = {}
# Store is a dictionary that maps addresses to their values
# e.g. 
store = {}
# Self Object should be void
self_object = Void()

my_exp = Dynamic_Dispatch(0, Exp(0,"new", "Main"), "main", [])

(new_value, new_store) = eval(self_object, store, env, my_exp)