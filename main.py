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
class LT(namedtuple("lt", "loc left_exp right_exp")): pass
class LE(namedtuple("le", "loc left_exp right_exp")): pass
class Negate(namedtuple("Negate", "loc exp")): pass
class Equal(namedtuple("Equal", "loc left_exp right_exp")): pass
class Times(namedtuple("Times", "loc left_exp right_exp")): pass
class Divide(namedtuple("Divide", "loc left_exp right_exp")): pass
class Minus(namedtuple("Minus", "loc left_exp right_exp")): pass
class Plus(namedtuple("Plus", "loc left_exp right_exp")): pass
class Not(namedtuple("Not", "loc exp")): pass
class Integer(namedtuple("Integer", "loc exp")): pass 
class String(namedtuple("String", "loc exp")): pass
class If(namedtuple("If", "loc predicate then else_exp")): pass
class Block(namedtuple("Block", "loc expList")): pass
class While(namedtuple("While", "loc pred body")) : pass
class Let(namedtuple("Let", "loc body binding_list")): pass
class Binding(namedtuple("Binding", "id type exp")): pass
class Case(namedtuple("Case", "loc case_exp case_elem_list")): pass
class CaseElement(namedtuple("CaseElement", "loc var type body")):  pass
class true(namedtuple("true", "loc exp")): pass
class false(namedtuple("false", "loc exp")): pass
class Identifier(namedtuple("Identifier", "loc exp")): pass
class Object(namedtuple("Object", "loc exp")): pass
class Int(namedtuple("Int", "loc exp")): pass
class SELF_TYPE(namedtuple("SELF_TYPE", "loc exp")): pass
class Assign(namedtuple("Assign", "loc var exp")): pass
class SelfDispatch(namedtuple("SelfDispatch", "loc methodName exp")): pass
class DynamicDispatch(namedtuple("DynamicDispatch", "loc e methodName exp")): pass
class StaticDispatch(namedtuple("StaticDispatch", "loc e type methodName exp")): pass

class CoolValue(namedtuple("CoolValue", "className type value")): pass 
class CoolInt(namedtuple("CoolInt", "className attrs_and_locs value loc"), FieldUpdate): pass 
class CoolString(namedtuple("CoolString", "className attrs_and_locs value length loc"), FieldUpdate): pass 
class CoolBool(namedtuple("CoolString", "className attrs_and_locs value loc"), FieldUpdate): pass 
class CoolObject(namedtuple("CoolObject", "className attrs_and_locs loc"), FieldUpdate): pass
class InternalMethod(namedtuple("InternalMethod", "loc methodName return_type parent")) : pass

class Void(namedtuple("Void", "className")) : pass

INT_MAX_VALUE = 2147483647
INT_MIN_VALUE = 2147483648

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

def populate_ast_sections():
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
	return current_section

populate_ast_sections()
# Deserialize the class_map
class_map = {}
imp_map = {}
parent_map = {}

def read(e):
	this_line = e[0]
	del e[0]
	return this_line

def read_id(e):
	loc = read(e)
	name = read(e)
	return Identifier(loc, name)

def read_internal_exp(e):
	loc = read(e)  
	return_type = read(e) # what kind of expression
	_ = read(e) # 'internal' ast label
	body = read(e)	
	method_name = "".join(body.split(".")[1])
	parent = body.split(".")[0]
	return InternalMethod(loc, method_name, return_type, parent)

def read_binding(e):
	bkind = read(e)
	if bkind == "let_binding_init":
		binding_id = read_id(e)
		binding_id_type = read_id(e)
		binding_exp = read_exp(e)
		return Binding(binding_id, binding_id_type, binding_exp)
	else:
		binding_id = read_id(e)
		binding_id_type = read_id(e)
		return Binding(binding_id, binding_id_type, None)

def read_exp(e):
	debug(f"expression is {str(e)}")
	if e[1][0].isupper():
		debug("got to upper")
		loc = read(e)
		_ = read(e)
		e_kind = read(e)
	else: # from ast, the extra class name we add that serves as a type
		loc = read(e)
		e_kind = read(e)
  
	if e_kind == "identifier":
		return read_id(e)
	elif e_kind == "not":
		return Not(loc, read_exp(e))
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
		method_name = read_id(e)
		file_name = method_name.exp
		num_of_args = int(read(e))
		args = [read_exp(e) for _ in range(num_of_args)]
		return SelfDispatch(loc, file_name, args)
	elif e_kind == "dynamic_dispatch":
		e0 = read_exp(e)
		method_name = read_id(e)
		file_name = method_name.exp
		num_of_args = int(read(e))
		args = [read_exp(e) for _ in range(num_of_args)]
		return DynamicDispatch(loc, e0, file_name, args)
	elif e_kind == "static_dispatch":
		e0 = read_exp(e)	
		static_type = read_id(e)
		method_name = read_id(e)
		num_of_args = int(read(e))
		arg_list = [read_exp(e) for _ in range(num_of_args)]
		return StaticDispatch(loc, e0, static_type.exp, method_name.exp, arg_list)
	elif e_kind == "true":
		return true(loc, "true")
	elif e_kind == "false":
		return false(loc, "false")
	elif e_kind == "negate":
		exp = read_exp(e)
		return Negate(loc, exp)
	elif e_kind == "times":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return Times(loc,left_exp,  right_exp)
	elif e_kind == "divide":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return Divide(loc,left_exp,  right_exp)
	elif e_kind == "plus":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return Plus(loc,left_exp,  right_exp)
	elif e_kind == "minus":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return Minus(loc,left_exp,  right_exp)
	elif e_kind == "le":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return LE(loc,left_exp,  right_exp)	
	elif e_kind == "lt":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return LT(loc,left_exp, right_exp)
	elif e_kind == "eq":
		left_exp = read_exp(e)
		right_exp = read_exp(e)
		return Equal(loc,left_exp, right_exp)
	elif e_kind == "if":
		pred = read_exp(e)
		then = read_exp(e)
		else_s = read_exp(e)
		return If(loc, pred, then, else_s)
	elif e_kind == "block":
		exp_count = int(read(e))
		debug(f"exp count is {exp_count}")
		all_exps = [read_exp(e) for _ in range(exp_count)]
		return Block(loc,  all_exps)
	elif e_kind == "while":
		pred = read_exp(e)
		body = read_exp(e)
		return While(loc, pred, body)
	elif e_kind == "case":
		exp = read_exp(e)
		num_elems = int(read(e))
		case_elem_list = []
		for _ in range(num_elems):
			var = read_id(e)
			type = read_id(e)
			body = read_exp(e)
			case_elem_list.append(CaseElement(0, var, type, body))
		return Case(loc, exp, case_elem_list)
	elif e_kind == "let":
		num_bindings = int(read(e))
		binding_list = [read_binding(e) for _ in range(num_bindings)]
		body = read_exp(e)
		return Let(loc, body, binding_list)
	elif e_kind == "not":
		return Not(loc, read_exp(e))
	else:
		print(f"e_kind not handled {e_kind}")
		exit(0)

def populate_parent_map(parent_map_ast):
	num_classes = int(read(parent_map_ast))		
	for _ in range(num_classes):
		parent_map[read(parent_map_ast)] = read(parent_map_ast)
		num_classes -= 1
  	
def populate_class_map(class_map_ast):
	num_classes = int(read(class_map_ast))
	for _ in range(num_classes):
		class_name = read(class_map_ast)
		num_attributes = int(read(class_map_ast))
		debug(f"num of attributes {num_attributes}")
		attributes = []
		for _ in range(num_attributes):
			is_init = read(class_map_ast)
			att_name = read(class_map_ast)
			att_type = read(class_map_ast)
			if is_init == "initializer":
				attributes.append((att_name, att_type, read_exp(class_map_ast)))
			
			attributes.append((att_name, att_type, []))
		class_map[class_name] = attributes
                
def populate_imp_map(imp_map_ast):
	num_classes = int(read(imp_map_ast))
	for _ in range(num_classes):
		class_name = read(imp_map_ast)
		num_methods = int(read(imp_map_ast))
		for _ in range(num_methods):
			method_name = read(imp_map_ast)
			num_formals = int(read(imp_map_ast))
			formal_list = [read(imp_map_ast) for _ in range(num_formals)]
			_ = read(imp_map_ast) #parent class
			if imp_map_ast[2] == "internal":
				m_body = read_internal_exp(imp_map_ast)
			else:
				m_body = read_exp(imp_map_ast)

			imp_map[(class_name,method_name)] = (formal_list, m_body)


# first index is label (class_map, parent_map, implementation_map) etc
populate_parent_map(parent_map_ast[1:])
populate_class_map(class_map_ast[1:])
populate_imp_map(imp_map_ast[1:])

new_location_counter = 1000
def newloc():
	global new_location_counter
	new_location_counter += 1	
	return new_location_counter

def default_value(typename):
	if typename == "Int":
		return CoolInt("Int", {}, 0, 0)
	elif typename == "String":
		return CoolString("String", {}, "", 0, 0)
	elif typename == "Bool":
		return CoolBool("Bool", {}, False, 0)
	else:
		return Void("RETURNED VOID") 

def eval(self_object, store, env, exp):
	global indent_count
	indent_count += 2
	debug(f"eval: {str(exp)}")
	debug(f"so: {str(self_object)}")
	debug(f"store: {str(store)}")
	debug(f"env: {str(env)}")
	debug(f"exp: {str(exp)}")

	if isinstance(exp, New): 
		debug(f"IN NEW\n")
		class_name = exp.exp
		if class_name == "SELF_TYPE":
			class_name = self_object.className
		else:
			class_name = exp.exp
		debug(f"class map is {str(class_map)}")
		attr_and_inits = class_map[class_name]
		new_attrs_locs = [newloc() for _ in attr_and_inits]

		attr_names = []
		for at in attr_and_inits:
			attr_names.append(at[0])

		attrs_and_locs = dict(zip(attr_names, new_attrs_locs))
		debug(f"CLASS NAME {str(class_name)}")
		if class_name in ["String", "Int", "Bool"]:
			v1 = default_value(class_name)
			debug(f"TESTING L;AH {str(v1)}")
			v1 = v1._replace(attrs_and_locs = attrs_and_locs)
		else:
			v1 = CoolObject(class_name, attrs_and_locs, 0)
		debug(f"IN NEW ATTRS AND LOC IS {str(attrs_and_locs)}")
		s2 = copy.deepcopy(store)
			
		for attr_name in attrs_and_locs.keys():
			attr_loc = attrs_and_locs[attr_name]
			for (attr_name2, attr_type, _) in attr_and_inits:
				if attr_name == attr_name2:
					s2[attr_loc] = default_value(attr_type)
					# s2[attr_loc] = s2[attr_loc]._replace(loc = attr_loc)

		final_store = s2
		for (attr_name,_,attr_init) in attr_and_inits:
			if attr_init != []:
				(_,curr_store) = eval(v1, final_store, attrs_and_locs, Assign(0,attr_name, attr_init))
				final_store = curr_store

		debug(f"ret = {str(v1)}")
		debug(f"rets = {str(final_store)}")
		indent_count -= 2
		return (v1,final_store)
	elif isinstance(exp, Assign):
		debug("IN ASSIGN\n")
		(v1, s2) = eval(self_object, store, env, exp.exp)	
		l1 = env[exp.var]	
		del s2[l1]
		s3 = s2
		s3[l1] = v1 # replace s2's l1 with v1
	
		v1 = v1._replace(loc = l1)
		debug(f"ret = {(v1)}")
		debug(f"rets = {(s3)}")
		indent_count -= 2
		return (v1, s3)
	elif isinstance(exp, SelfDispatch):
		debug("IN SELF DISPATCH\n")
		# call dynamic_dispatch, but use the self object as receiver exp
		self_exp = Identifier(0, "self")
		ret_exp = DynamicDispatch(exp.loc, self_exp, exp.methodName, exp.exp)
		(ret_value,ret_store) = eval(self_object, store, env, ret_exp)
		debug(f"ret = {str(ret_value)}")
		debug(f"rets = {str(ret_store)}")
		indent_count -= 2
		return (ret_value, ret_store)
	elif isinstance(exp, DynamicDispatch):
		debug("IN DYNAMIC DISPATCH\n")
		curr_store = copy.deepcopy(store)
		arg_values = []
		# eval each arg while updating store
		for arg in exp.exp:
			(arg_value, new_store) = eval(self_object, curr_store, env, arg)
			curr_store = new_store
			arg_values.append(arg_value)

		# eval receiver expression
		(v0, s_n2) = eval(self_object, curr_store, env, exp.e)
		debug(f"vo is {v0}")
		if (v0.className, exp.methodName) not in imp_map:
			print(f"ERROR: {str(loc)}: Exception: dispatch on void")
			sys.exit(0)
		(formals, body) = imp_map[(v0.className, exp.methodName)]
		# allocate mem for each args
		new_arg_locs = [ newloc() for _ in formals]
		s_n3 = s_n2
		store_update = dict(zip(new_arg_locs, arg_values))
		for loc in store_update.keys(): 
			value = store_update[loc]
			value = value._replace(loc = loc)
			s_n3[loc] = value
			
		new_enviroment = copy.deepcopy(v0.attrs_and_locs)
	 
		env_update = dict(zip(formals, new_arg_locs))
		for (identifier,loc) in env_update.items():
			new_enviroment[identifier] = loc

		(ret_value, ret_store) = eval(v0, s_n3, new_enviroment, body)
		debug(f"ret = {str(ret_value)}")
		debug(f"rets = {str(ret_store)}")
		indent_count -= 2
		return (ret_value,ret_store)
	elif isinstance(exp, StaticDispatch):
		debug("IN STATIC DISPATCH\n")
		curr_store = copy.deepcopy(store)
		arg_values = []

		for arg in exp.exp:
			(arg_value, new_store) = eval(self_object, curr_store, env, arg)
			curr_store = new_store
			arg_values.append(arg_value)
		(v0, s_n2) = eval(self_object, curr_store, env, exp.e)
		(formals, body) = imp_map[(exp.type, exp.methodName)]
		new_arg_locs = [newloc() for f in formals]
		s_n3 = s_n2
		new_store = dict(zip(new_arg_locs, arg_values))
		for new_loc in new_store.keys():
			value = new_store[loc]
			value = value._replace(loc = new_loc)
			s_n3[new_loc] = value

		new_env = copy.deepcopy(v0.attrs_and_locs)
		env_update = dict(zip(formals, new_arg_locs))
		for id in env_update.keys():
			new_env[id] = env_update[id]
		debug(f"ENV UPDATE IS {str(env_update)})")

		(ret_value, ret_store) = eval(v0, s_n3, new_env, body)
		debug(f"ret = {ret_value}")
		debug(f"rets = {ret_store}")
		indent_count -= 2
		return (ret_value, ret_store)
	elif isinstance(exp, Plus): 
		debug("IN PLUS\n")
		v1, s2 = eval(self_object,store,env,exp.left_exp)
		v2, s3 = eval(self_object,store,env,exp.right_exp)
		new_value = v1.value + v2.value
		if new_value > INT_MAX_VALUE:
			new_value -= INT_MIN_VALUE
			new_value += -INT_MIN_VALUE
		elif new_value < -INT_MIN_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE

		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, new_value, 0), store)
	elif isinstance(exp, Minus): 
		debug("IN MINUS\n")
		v1, s2 = eval(self_object,store,env,exp.left_exp)
		v2, s3 = eval(self_object,store,env,exp.right_exp)
		new_value = v1.value - v2.value
		if new_value < -INT_MIN_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		elif new_value > -INT_MAX_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, new_value, 0), store)
	elif isinstance(exp, Times): 
		debug("IN TIMES\n")
		v1, s2 = eval(self_object,store,env,exp.left_exp)
		v2, s3 = eval(self_object,store,env,exp.right_exp)
		new_value = v1.value * v2.value
		if new_value > INT_MAX_VALUE:
			new_value -= INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		elif new_value < -INT_MIN_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, new_value, 0), store)
	elif isinstance(exp, Divide): 
		debug("IN DIVIDE\n")
		v1, s2 = eval(self_object,store,env,exp.left_exp)
		v2, s3 = eval(self_object,store,env,exp.right_exp)
		if v2.value == 0: # can't do divide by 0
			print(f"ERROR: {exp.left_exp.loc}: Exception: division by zero")
			sys.exit(0)
		new_value = v1.value / v2.value
		if new_value > INT_MAX_VALUE:
			new_value -= INT_MIN_VALUE
			new_value += -INT_MIN_VALUE
		elif new_value < -INT_MIN_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, new_value, 0), store)
	
	elif isinstance(exp, Negate):
		debug("IN NEGATE\n")
		v1, s2 = eval(self_object,store,env,exp.exp)
		new_value = -v1.value
		if new_value < -INT_MIN_VALUE:
			new_value += INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		elif new_value > INT_MAX_VALUE:
			new_value -= INT_MIN_VALUE
			new_value += INT_MIN_VALUE
		debug(f"ret = {str(new_value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, new_value, 0), s2)
	elif isinstance(exp, Integer):
		debug("IN INTEGER\n")
		value = int(exp.exp)
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolInt("Int", {}, value, 0), store)
	elif isinstance(exp, String):
		debug("IN STRING\n")
		value = str(exp.exp)
		length = len(value)
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (CoolString("String", {}, value, length, 0), store)
	elif isinstance(exp, Identifier):
		debug("IN IDENTIFIER\n")
		debug(f"env here is {str(env)}")
		id = exp.exp
		if id == "self":
			return (self_object,store)
		loc = env[id]
		value = store[loc]
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(store)}")
		indent_count -= 2
		return (value,store)
	elif isinstance(exp, InternalMethod):
		debug("IN INTERNAL\n")
		if exp.methodName == "out_string":
			val = str(store[env['x']].value)		
			print(val.replace("\\n", "\n").replace("\\t", "\t"), end="")
			return self_object, store
		elif exp.methodName == "out_int":
			val = store[env['x']].value	
			 # x is the arg for out_int, i.e. out_int(x)
			print(val, end=" ")
			return self_object, store
		elif exp.methodName == "in_string":
			try:
				read_line = input()
				if '\x00' in read_line: # might fail
					return CoolString("String", {}, "", 0), store
				else:
					return CoolString("String", {}, read_line, 0), store
			except EOFError:
				return CoolString("String", {}, "", 0), store
		elif exp.methodName == "in_int":
			try:
				read_line = input()
				read_line = read_line.strip()
				
				numbers = ""
				for c in read_line:
					if c.isdigit():
						numbers += c
					else:
						break
				if len(numbers) == 0: # input didnt start with numbers
					return CoolInt("Int", {}, 0, 0), store
				
				if int(numbers) > 2147483647 or int(numbers) < -2147483648: #check range
					return CoolInt("Int", {}, 0, 0), store
				else:
					return CoolInt("Int", {}, int(numbers), 0), store

			except EOFError:
				return CoolInt("Int", {}, 0, 0), store

		elif exp.methodName == "length":
			return CoolInt("Int", {}, self_object.length, 0)
		elif exp.methodName == "concat":
			pass
		elif exp.methodName == "substr":
			pass
		elif exp.methodName == "abort": # TODO THIS DOESNT WORK YET
			print("abort")
			sys.exit(0)
		elif exp.methodName == "copy":
			pass
		elif exp.methodName == "type_name":
			class_name = self_object.className
			return CoolString(class_name, {}, class_name, len(class_name), 0), store
		
	elif isinstance(exp, IsVoid):
		debug("In ISVOID\n")
		v1, s2 = eval(self_object, store, env, exp.exp)
		is_void = isinstance(v1, Void)
		return CoolBool("CoolBool", {}, is_void, 0), s2
	
	elif isinstance(exp, Case):
		debug("IN CASE\n")
		v0, s2 = eval(self_object, store, env,  exp.exp)

	elif isinstance(exp, Not):
		debug("IN NOT\n")
		v1, s2 = eval(self_object, store, env, exp.exp)
		neg = "true" if v1.value == False else "false"
		return CoolBool("CoolBool", {}, neg, 0), s2
	elif isinstance(exp, Equal):
		debug("IN EQUAL\n")
		(i1, s2) = eval(self_object, store, env, exp.left_exp)
		(i2, s3) = eval(self_object, store, env, exp.right_exp)
		if i1.value == i2.value:
			v1 = CoolBool("CoolBool", {}, True, 0)
			return (v1, s3)
		else:
			v1 = CoolBool("CoolBool", {}, False, 0)
			return (v1, s3)
	elif isinstance(exp, LE):
		debug("IN LE\n")
		(i1, s2) = eval(self_object, store, env, exp.left_exp)
		(i2, s3) = eval(self_object, store, env, exp.right_exp)
		if i1.value <= i2.value:
			v1 = CoolBool("CoolBool", {}, True, 0)
			return (v1, s3)
		else:
			v1 = CoolBool("CoolBool", {}, False, 0)
			return (v1, s3)
	elif isinstance(exp, LT):
		debug("IN LT\n")
		(i1, s2) = eval(self_object, store, env, exp.left_exp)
		(i2, s3) = eval(self_object, store, env, exp.right_exp)
		if i1.value < i2.value:
			v1 = CoolBool("CoolBool", {}, True, 0)
			return (v1, s3)
		else:
			v1 = CoolBool("CoolBool", {}, False, 0)
			return (v1, s3)
	elif isinstance(exp, false):
		debug("IN FALSE\n")
		return (CoolBool("CoolBool", {}, False, 0), store)
	elif isinstance(exp, true):
		debug("IN TRUE\n")
		return (CoolBool("CoolBool", {}, True, 0), store)
	elif isinstance(exp, If): #yonas
		debug("IN IF\n")
		#true and false conditions
		pred = exp.predicate
		(value, new_store) = eval(self_object, store, env, pred)
		debug(f"ret = {str(value)}")
		debug(f"rets = {str(new_store)}")
		if value.value == True:
			#eval the then expression
			return  eval(self_object, new_store, env,exp.then)
		else:
			return eval(self_object, new_store, env, exp.else_exp)
			#eval the else expression

	elif isinstance(exp, While): #yonas
		debug("IN WHILE\n")
		pred = exp.pred
		(v1, s2) = eval(self_object, store, env, pred)
		if v1.value == True:
			#recursive until val returned is false
			(v3, s3) = eval(self_object, s2, env, exp.body) 
			while_rep = While(exp.loc, pred, exp.body)
			debug(f"v3 from while is {v3}")
			# we want just the last one tho
			return eval(self_object, s3, env, while_rep)
		else:
			return (Void("void"), s2)

	elif isinstance(exp, Let):
		debug("IN LET\n")
		# go through bindings and update
		e_prime = copy.deepcopy(env)
		for binding in exp.binding_list:
			env_id = binding.id.exp
			e1 = binding.exp
			v1, store = eval(self_object, store, env,e1)
			l1 = newloc()
			store[l1] = v1
			e_prime[env_id] = l1

		#body expression eval
		v2, store = eval(self_object, store, e_prime, exp.body)
		debug(f"ret = {str(v2)}")
		debug(f"rets = {str(store)}")
		return v2, store
			
	elif isinstance(exp, Binding):
		debug("IN BINDING\n")
		debug("SHOULD NEVER GET HERE\n")
		return self_object, store
	elif isinstance(exp, Block):
		debug("IN BLOCK\n")  
		s1 = store
		for exp in exp.expList:
			ret_value, ret_store = eval(self_object, s1, env, exp)
			s1 = ret_store

		indent_count -= 2
		return (ret_value, s1)
	
	elif isinstance(exp, CoolObject):
		debug("COOL OBJECT ___-----\n")
		return self_object, store		
	else:
		# print(f"unhandled exp for {exp}")
		exit(0)
	

# cool entry point is Main's main method
entry_point = DynamicDispatch(0, New(0, "Main"), "main", [])
(new_value, new_store) = eval(Void("ENTRY"), {}, {}, entry_point)
# print((new_value, new_store))




