

for property in obj.properties:
	print property.name
	print property.description
	print getattr(obj, property.name)
	

obj.Positional.Velocity.relativeto = 99
assert obj.Positional.Velocity.relativeto = 99

assert type(obj.Positional.Velocity) == orderParamAbsSpaceCoords

obj.Positional.Velocity.pos = [0, 8, 9]
assert obj.Positional.Velocity.pos.x == 0
assert obj.Positional.Velocity.pos.y == 8
assert obj.Positional.Velocity.pos.z == 9
obj.Positional.Velocity.pos.x = 10
obj.Positional.Velocity.pos.y = 11
obj.Positional.Velocity.pos.z = 12
assert obj.Positional.Velocity.pos = [10, 11, 12]

# These should fail
obj.Positional.Velocity.pos = 1
obj.Positional.Velocity.pos.x = "test"

obj.Positional.Size = 100000
assert obj.Positional.Size == 100000


obj.Informational.Year = 99

