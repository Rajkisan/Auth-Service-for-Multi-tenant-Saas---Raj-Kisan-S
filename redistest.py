import redis

r=redis.Redis(host='localhost',port=6379)

r.set('france','paris')

r.set('paris','netherland')

print(r.get('paris'))
