import mayavi.mlab as mlab
import numpy as np

data = scipy.io.loadmat('./data_NC/NC_cortex.mat',struct_as_record = True)
brain = data['cortex']['vert'][0,0]
tri = data['cortex']['tri'][0,0]

mlab.triangular_mesh(brain[:,0],brain[:,1],brain[:,2],tri)




handle=trisurf(struct.tri, struct.vert(:, 1), struct.vert(:, 2), struct.vert(:, 3), ...
         'FaceVertexCData', col, varargin{:});



ctmr_gauss_plot(cortex,[0 0 0], 0)

gsp=50;

c=zeros(length(cortex(:,1)),1);
for i=1:length(electrodes(:,1))
    b_z=abs(brain(:,3)-electrodes(i,3));
    b_y=abs(brain(:,2)-electrodes(i,2));
    b_x=abs(brain(:,1)-electrodes(i,1));
%     d=weights(i)*exp((-(b_x.^2+b_z.^2+b_y.^2).^.5)/gsp^.5); %exponential fall off 
    d=weights(i)*exp((-(b_x.^2+b_z.^2+b_y.^2))/gsp); %gaussian 
    c=c+d';
end

% c=(c/max(c));
a=tripatch(cortex, '', c');