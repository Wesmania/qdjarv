class ValidationError(Exception):
    pass


class Rel:
    def __init__(self, type_):
        self.type_ = type_


def Type(t):

    def v(obj):
        if not isinstance(obj, t):
            raise ValidationError(f"Expected type '{t}', got '{type(obj)}'")
        return obj

    return v


class Parser:
    def __init__(self, top, types, include=None, fields=None):
        self.top = top
        self.types = types
        self.include = include if include is not None else {}
        self.fields = fields if fields is not None else {}

    def fields_args(self):
        return [f"fields[{k}]={','.join(vs)}" for k, vs in self.fields.items()]

    def include_args(self, include=None, pfx=""):
        res = []
        if include is None:
            include = self.include
        for k, v in include.items():
            res.append(pfx + k)
            res += self.include_args(v, f"{pfx}{k}.")
        return res

    def _check_is_list(self, spec, item):
        is_list = isinstance(spec, list)
        should_be_list = isinstance(item, list)
        if should_be_list and not is_list:
            raise ValidationError("Expected list, got singleton")
        if not should_be_list and is_list:
            raise ValidationError("Expected singleton, got list")
        return should_be_list

    def _validate_top(self, obj):
        if self._check_is_list(self.top, obj):
            top = self.top[0]
            for o in obj:
                if o["type"] != top:
                    raise ValidationError(
                        f"Expected [{self.top}], but top has type {o['type']}")
        else:
            if obj["type"] != self.top:
                raise ValidationError(
                    f"Expected {self.top}, but top has type {obj['type']}")

    def _rename(self, obj, attr):
        # Conveniently, names with dots are disallowed by jsonapi.
        if attr in obj:
            obj["." + attr] = obj.pop(attr)

    def _flatten_object(self, obj):
        self._rename(obj, "relationships")
        self._rename(obj, "attributes")
        self._rename(obj, "links")
        self._rename(obj, "meta")
        rels = obj.get(".relationships", {})
        fields = obj.get(".attributes", {})
        obj.update(rels)
        obj.update(fields)

    def _parse_one(self, obj):
        self._flatten_object(obj)
        ot = obj["type"]
        if ot not in self.types:
            raise ValidationError(f"Unknown type '{ot}'")

        f_filter = self.fields.get(ot)
        o_fields = self.types[ot]
        for f, f_type in o_fields.items():
            if f_filter is not None and f not in f_filter:
                continue
            self._validate_field(obj, f, f_type)

    def _validate_field(self, obj, f, f_type):
        if isinstance(f_type, Rel):
            self._validate_rel(obj, f, f_type)
        else:
            self._validate_attr(obj, f, f_type)

    def _validate_rel(self, obj, f, f_type):
        ot = obj["type"]
        f_data = obj.get(".relationships", {}).get(f)
        if f_data is None:
            raise ValidationError(f"Relationship '{f}' not found for '{ot}'")
        if "data" not in f_data:
            return

        data = f_data["data"]
        if self._check_is_list(f_type.type_, data):
            rel_type = f_type.type_[0]
            for d in data:
                if d["type"] != rel_type:
                    raise ValidationError(
                        f"Expected type '{rel_type}', got '{d['type']}'")
        else:
            if data is None:
                return
            rel_type = f_type.type_
            if data["type"] != rel_type:
                raise ValidationError(
                    f"Expected type '{rel_type}', got '{data['type']}'")

    def _validate_attr(self, obj, f, f_type):
        ot = obj["type"]
        if ".attributes" not in obj or f not in obj[".attributes"]:
            raise ValidationError(f"Field '{f}' not found for '{ot}'")
        f_data = obj[".attributes"][f]
        obj[f] = f_type(f_data)

    def _link(self, objs):
        obj_dict = {
            (obj["id"], obj["type"]): obj
            for obj in objs
        }
        for obj in objs:
            self._link_one(obj, obj_dict)

    def _link_one(self, obj, obj_dict):
        if ".relationships" not in obj:
            return

        def lookup(ref):
            if ref is None:
                return ref
            key = (ref["id"], ref["type"])
            return obj_dict.get(key, ref)

        for rel, v in obj[".relationships"].items():
            if "data" not in v:
                continue
            if isinstance(v["data"], list):
                v["data"] = [lookup(d) for d in v["data"]]
            else:
                v["data"] = lookup(v["data"])

    def _verify_includes(self, data):
        self._verify_includes_rec(data, self.include)

    def _verify_includes_rec(self, obj, spec):
        if isinstance(obj, list):
            for o in obj:
                self._verify_includes_rec(o, spec)
        else:
            # Assume all include fields are verified as present.
            for f, sub in spec.items():
                if f not in obj or "data" not in obj[f]:
                    raise ValidationError(f"Field {f} was not included")
                data = obj[f]["data"]
                if data is None:    # Null one-to-one rel
                    return
                if isinstance(data, list):
                    to_check = data
                else:
                    to_check = [data]
                for d in to_check:
                    if set(d.keys()) == {"id", "type"}:
                        raise ValidationError(f"Field {f} was not included")
                self._verify_includes_rec(data, sub)

    def parse(self, message):
        all_objects = []

        if "data" in message:
            d = message["data"]
            self._validate_top(d)
            if isinstance(d, list):
                for v in d:
                    self._parse_one(v)
                all_objects += d
            else:
                self._parse_one(d)
                all_objects.append(d)

        if "included" in message:
            d = message["included"]
            for v in d:
                self._parse_one(v)
            all_objects += d

        self._link(all_objects)
        self._verify_includes(message["data"])
        return message
