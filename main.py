import sys
import copy

from collections import namedtuple


class FieldUpdate():
    def set_attrs_and_locs(self, st): 
        self.st = st
    def get_attrs_and_locs(self): 
        try:
            return self.st
        except:
            pass
    
        
class New(namedtuple("New", "loc exp")): pass
class IsVoid(namedtuple("IsVoid", "loc exp")): pass
class LT(namedtuple("lt", "loc exp")): pass
class LE(namedtuple("le", "loc exp")): pass
class Negate(namedtuple("Negate", "loc exp")): pass
class Equal(namedtuple("Equal", "loc exp")): pass
class Times(namedtuple("Times", "loc exp")): pass
class Divide(namedtuple("Divide", "loc exp")): pass
class Times(namedtuple("Times", "loc exp")): pass
class Minus(namedtuple("Minus", "loc exp")): pass
class Plus(namedtuple("Plus", "loc exp")): pass
class Not(namedtuple("Not", "loc exp")): pass
class Integer(namedtuple("Integer", "loc exp")): pass 
class String(namedtuple("String", "loc exp")): pass
class true(namedtuple("true", "loc exp")): pass
class false(namedtuple("false", "loc exp")): pass
class Identifier(namedtuple("Identifier", "loc exp")): pass
class Object(namedtuple("Object", "loc exp")): pass
class Int(namedtuple("Int", "loc exp")): pass
class IO(namedtuple("IO", "loc exp")): pass
class SELF_TYPE(namedtuple("SELF_TYPE", "loc exp")): pass
class Assign(namedtuple("Assign", "loc var exp")): pass
class SelfDispatch(namedtuple("SelfDispatch", "loc methodName exp")): pass
class DynamicDispatch(namedtuple("DynamicDispatch", "loc e methodName exp")): pass
class CoolValue(namedtuple("CoolValue", "type value")): pass 
class CoolInt(namedtuple("CoolInt", "className attrs_and_locs loc value"), FieldUpdate): pass 
class CoolString(namedtuple("CoolString", "className attrs_and_locs loc value length"), FieldUpdate): pass 
class CoolBool(namedtuple("CoolString", "className attrs_and_locs loc value"), FieldUpdate): pass 
class CoolObject(namedtuple("CoolObject", "className attrs_and_locs loc"), FieldUpdate): pass

class Void(namedtuple("Void", "className")) : pass

# Debugging and Tracing
do_debug = False
global indent_count
indent_count = 0
	
def debug(e): 
	global indent_count
	if do_debug:
		print()
		print(' ' * indent_count, end ="")
	if do_debug:
		print(e)

file_name = sys.argv[1]

# Read in the annotated ast
ast_file = []
with open(file_name, 'r') as f:
	for line in f:
		line = line.rstrip()
		ast_file.append(line)

class_map_ast = []
parent_map_ast = []
imp_map_ast = []

current_section = None

for line in ast_file:
    if line == "implementation_map":
        current_section = imp_map_ast
    elif line == "parent_map":
        current_section = parent_map_ast
    elif line == "class_map":
        current_section = class_map_ast
    
    if current_section is not None:
        current_section.append(line)

# Deserialize the class_map
class_map = {}
imp_map = {}


def read(e):
	this_line = e[0]
	del e[0]
	return this_line

def read_exp_list(method,num_args):
	return [method for _ in range(num_args)]

def read_id(e):
	loc = read(e)
	name = read(e)
	return Identifier(loc, name)

def read_internal_exp(e):
	loc = read(e)  
	_ = read(e) #what kind of expression
	_ = read(e) # 'internal' ast label
	body = read(e)	
	return SELF_TYPE(loc, body) #TODO : this is hardcoded


def read_exp(e):
	loc = read(e)
	_ = read(e) # expression type
	e_kind = read(e)
	# create namedtuple object based on expression kind
 
	if e_kind == "identifier":
		return read_id(e)
	elif e_kind == "isvoid":
		return IsVoid(loc, read_exp(e))		# return t
	elif e_kind == "string":
		str_constant = read(e) 
		return String(loc, str_constant)
	elif e_kind == "integer":
		int_constant = read(e)
		return Integer(loc, int_constant)
	elif e_kind == "assign":
		var = read_id(e)
		return Assign(loc,var.exp,read_exp(e))
	elif e_kind == "new":
		id_ver = read_id(e) 
		return New(id_ver.loc, id_ver.exp)
	elif e_kind == "self_dispatch":
		funcid = read_id(e)
		file_name = funcid.exp
		num_of_args = int(read(e))
		return SelfDispatch(loc, file_name,read_exp_list(read_exp(e),num_of_args))
	elif e_kind == "dynamic_dispatch":
		e0 = read_exp(e)
		funcid = read_id(e)
		file_name = funcid.exp
		num_of_args = int(read(e))
		return DynamicDispatch(loc, e0, file_name, read_exp_list(read_exp(e),num_of_args))
	else:
		print(f"e_kind not handled {e_kind}")
		exit(0)
	
def populate_class_map(class_map_ast):
    num_classes = int(read(class_map_ast))
    for i in range(num_classes):
        class_name = read(class_map_ast)
        num_attributes = int(read(class_map_ast))
        attributes = []
        for j in range(num_attributes):
            is_init = read(class_map_ast)
            att_name = read(class_map_ast)
            att_type = read(class_map_ast)
            if is_init == "initializer":
                attributes.append((att_name, att_type, read_exp(class_map_ast)))
            else:
                attributes.append((att_name, att_type, []))
        class_map[class_name] = attributes
                
def populate_imp_map(imp_map_ast):
	num_classes = int(read(imp_map_ast))
	for i in range(num_classes):
		class_name = read(imp_map_ast)
		num_methods = int(read(imp_map_ast))
		for j in range(num_methods):
			method_name = read(imp_map_ast)
			num_formals = int(read(imp_map_ast))
			formal_list = [read(imp_map_ast) for _ in range(num_formals)]
			_ = read(imp_map_ast) #parent class
			if imp_map_ast[2] == "internal":
				m_body = read_internal_exp(imp_map_ast)
			else:
				m_body = read_exp(imp_map_ast)
			imp_map[(class_name,method_name)] = (formal_list, m_body)


populate_class_map(class_map_ast[1:])
populate_imp_map(imp_map_ast[1:])

new_location_counter = 1000
def newloc():
	global new_location_counter
	new_location_counter += 1	
	return new_location_counter

def default_value(typename):
	if typename == "Int":
		return CoolInt("Int", {}, 0, 0, )
	elif typename == "String":
		return CoolString("String", {}, 0, "", 0)
	elif typename == "Bool":
		return CoolBool("Bool", {}, 0, False)
	else:
		return Void("RETURNED VOID") 


def eval(self_object,store,env,exp):
	global indent_count
	indent_count += 2
	debug(f"eval: {str(exp)}")
	debug(f"so: {str(self_object)}")
	debug(f"store: {str(store)}")
	debug(f"env: {str(env)}")
	debug(f"exp: {str(exp)}")

	if isinstance(exp, New): 
		class_name = exp.exp
		attr_and_inits = class_map[class_name]
		new_attrs_locs = [newloc() for _ in attr_and_inits]

		attr_names = []
		for at in attr_and_inits:
			attr_names.append(at[0])

		attrs_and_locs = dict(zip(attr_names, new_attrs_locs))
		v1 = CoolObject(class_name, attrs_and_locs, 0)
		s2 = copy.deepcopy(store)
			
		for attr_name in attrs_and_locs.keys():
			attr_loc = attrs_and_locs[attr_name]
			for (attr_name2, attr_type, _) in attr_and_inits:
				
				if attr_name == attr_name2:
					s2[attr_loc] = default_value(attr_type)

		final_store = s2
		for (attr_name,_,attr_init) in attr_and_inits:
			if attr_init != []:
				(_,current_store) = eval(v1, final_store, attrs_and_locs, Assign(0,attr_name, attr_init))
				final_store = current_store

		debug(f"ret = {str(v1)}")
		debug(f"rets = {str(final_store)}")
		indent_count -= 2
		return (v1,final_store)
	elif isinstance(exp, Assign):
		(v1, s2) = eval(self_object, store, env, exp.exp)	
		l1 = env[exp.var]	
		del s2[l1]
		s3 = s2
		s3[l1] = v1 # replace s2's l1 with v1
		debug(f"ret = {(v1)}")
		debug(f"rets = {(s3)}")
		indent_count -= 2
		return (v1,s3)
	elif isinstance(exp, SelfDispatch):
		# call dynamic_dispatch, but use the self object as receiver exp
		self_exp = Identifier(0, "self")
		ret_exp = DynamicDispatch(exp.loc, self_exp, exp.methodName, exp.exp)
		(ret_value,ret_store) = eval(self_object,store,env,ret_exp)
		debug(f"ret = {str(ret_value)}")
		debug(f"rets = {str(ret_store)}")
		indent_count -= 2
		return (ret_value,ret_store)
	elif isinstance(exp, DynamicDispatch):
		current_store = copy.deepcopy(store)
		arg_values = []
		# eval each arg while updating store
		for arg in exp.exp:
			(arg_value, new_store) = eval(self_object, current_store, env, arg)
			current_store = new_store
			arg_values.append(arg_value)

		if exp.methodName == "out_string": #TODO: handle other method, maybe modularize
			#replace \n str representation to actual \n
			print(arg_values[0].value.replace("\\n","\n"), end="")

		# eval receiver expression
		(v0, s_n2) = eval(self_object, current_store, env, exp.e)
		(formals, body) = imp_map[(v0.className, exp.methodName)]
		# allocate mem for each args
		new_arg_locs = [ newloc() for _ in exp.exp]
		s_n3 = s_n2
		store_update = dict(zip(new_arg_locs, arg_values))
		for loc in store_update.keys(): 
			s_n3[loc] = store_update[loc]
		new_enviroment = copy.deepcopy(v0.attrs_and_locs)
		env_update = dict(zip(formals, new_arg_locs))
		for (identifier,loc) in env_update.items():
			env_update[identifier] = loc
		(ret_value,ret_store) = eval(v0, s_n3, new_enviroment, body)
		debug(f"ret = {str(ret_value)}")
		debug(f"rets = {str(ret_store)}")
		indent_count -= 2
		return (ret_value,ret_store)
	elif isinstance(exp, Plus): 
		e1 = exp.exp[0]
		e2 = exp.exp[1]
		v1, s2 = eval(self_object,store,env,e1)
		v2, s3 = eval(self_object,store,env,e2)
		new_value = v1.value + v2.value
		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, 0, new_value), store)
	elif isinstance(exp, Integer):
		value = int(exp.exp)
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, 0, value), store)
	elif isinstance(exp, String):
		value = str(exp.exp)
		length = len(value)
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolString("String", {}, 0, value, length), store)
	elif isinstance(exp, Identifier):
		id = exp.exp
		if id == "self":
			return (self_object,store)
		loc = env[id]
		value = store[loc]
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (value,store)
	elif isinstance(exp, SELF_TYPE):
		return (self_object,store)
	elif isinstance(exp, IsVoid):
		pass
	elif isinstance(exp, false):
		pass
	elif isinstance(exp, true):
		pass
	else:
		print(f"unhandled exp for {exp}")
		exit(0)

# cool entry point is Main's main method
entry_point = DynamicDispatch(0, New(0, "Main"), "main", [])
(new_value, new_store) = eval(Void("ENTRY"), {}, {}, entry_point)









