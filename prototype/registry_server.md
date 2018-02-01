# How To Deploy a Registry Server

I recently had the need to understand how to deploy a docker registry server.
If you have a machine you want to act as an intermediary docker registry to
serve images to other hosts in your network, then this is the easiet way
to achieve that.

## Setting up the registry server
Pull the registry image that will be used to server images to hosts;
```
[root@registry ~]# docker pull docker.io/registry:2
Trying to pull repository docker.io/library/registry ...
sha256:9d295999d330eba2552f9c78c9f59828af5c9a9c15a3fbd1351df03eaad04c6a: Pulling from docker.io/library/registry
ab7e51e37a18: Pull complete
c8ad8919ce25: Pull complete
5808405bc62f: Pull complete
f6000d7b276c: Pull complete
f792fdcd8ff6: Pull complete
Digest: sha256:9d295999d330eba2552f9c78c9f59828af5c9a9c15a3fbd1351df03eaad04c6a
Status: Downloaded newer image for docker.io/registry:2
```
Start the registry image mapping port `5000` on the host to the container port
`5000`;
```
[root@registry ~]# docker run -d -p 5000:5000 --restart=always --name registry registry:2
2d2817b96b18a7483427a90a4d19295ca8b9626dc8fc3310b6c5509f802b143b
```
See that the registry container is now running;
```
[root@registry ~]# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
2d2817b96b18        registry:2          "/entrypoint.sh /etc/"   2 minutes ago       Up 2 minutes        0.0.0.0:5000->5000/tcp   registry
```
Push an image to your local registry e.g. `python-27-rhel7`
```
[root@registry ~]# docker images
REPOSITORY                                         TAG                 IMAGE ID            CREATED             SIZE
registry.access.redhat.com/rhscl/python-27-rhel7   latest              fa2da76ec949        3 days ago          628.5 MB
docker.io/registry                                 2                   177391bcf802        2 weeks ago         33.26 MB
```
By first tagging that image;
```
[root@registry ~]# docker tag registry.access.redhat.com/rhscl/python-27-rhel7 localhost:5000/rhscl/python-27-rhel7
```
And then pushing it to `localhost:5000` where the registry container is
listening;
```
[root@registry ~]# docker push localhost:5000/rhscl/python-27-rhel7
The push refers to a repository [localhost:5000/rhscl/python-27-rhel7]
bdeb00d0dbf4: Pushed
4aa29cc77c01: Pushed
b65a1e61499d: Pushed
02404b4d7e5d: Pushed
e1d829eddb62: Pushed
latest: digest: sha256:adc4c3f79cb5fa399dac4a9089df05873cd7f3994441782d353bf32107edb478 size: 1372
```
See the image is now hosted on the local registry, ready to be pulled by any
hosts that are pointed at the this registry;
```
[root@registry ~]# docker images
REPOSITORY                                         TAG                 IMAGE ID            CREATED             SIZE
registry.access.redhat.com/rhscl/python-27-rhel7   latest              fa2da76ec949        3 days ago          628.5 MB
localhost:5000/rhscl/python-27-rhel7               latest              fa2da76ec949        3 days ago          628.5 MB
docker.io/registry                                 2                   177391bcf802        2 weeks ago         33.26 MB
```

## Configuring hosts to point at the local registry
You should have a host running docker. Configure the host to block other
registries and only poing at your local registr. Securing your registry via
`tls` is a whole other thing so just make it an insecure registry for the
moment;
```
[root@master ~]# egrep '^ADD|^BLOCK|^INSECURE' /etc/sysconfig/docker
BLOCK_REGISTRY='--block-registry registry.access.redhat.com --block-registry docker.io'
ADD_REGISTRY='--add-registry registry.ocp.cluster:5000'
INSECURE_REGISTRY='--insecure-registry registry.ocp.cluster:5000'
```
Pull the image;
```
[root@master ~]# docker pull rhscl/python-27-rhel7
Using default tag: latest
Trying to pull repository registry.ocp.cluster:5000/rhscl/python-27-rhel7 ...
sha256:adc4c3f79cb5fa399dac4a9089df05873cd7f3994441782d353bf32107edb478: Pulling from registry.ocp.cluster:5000/rhscl/python-27-rhel7
9cadd93b16ff: Pull complete
4aa565ad8b7a: Pull complete
318bc687a5f9: Pull complete
d9bc842e4d5b: Pull complete
56afade32ff3: Pull complete
Digest: sha256:adc4c3f79cb5fa399dac4a9089df05873cd7f3994441782d353bf32107edb478
Status: Downloaded newer image for registry.ocp.cluster:5000/rhscl/python-27-rhel7:latest
```
See that the image was pulled;
```
[root@master ~]# docker images
REPOSITORY                                        TAG                 IMAGE ID            CREATED             SIZE
registry.ocp.cluster:5000/rhscl/python-27-rhel7   latest              fa2da76ec949        3 days ago          628.5 MB
```

## References

- [Deploying a registry server](https://docs.docker.com/registry/deploying/)
- [Docker Registry Image](https://hub.docker.com/_/registry/)
