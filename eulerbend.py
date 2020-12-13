
import pya
import numpy as np


def ecurvesym(rmin=10, theta=np.pi/2, n=50):
   #Reference https://en.wikipedia.org/wiki/Euler_spiral
    #normalized euler curve: l=1/r, theta=l/2/r;  
    theta2=theta/2
    ds=np.sqrt(theta2)/n #ds step for normalized euler curve, ~0.01 to give smooth curve
    #n=int(np.sqrt(theta2)/ds) #number of points determined by thetamax and ds
    x=np.zeros(n)
    y=np.zeros(n)
    for i in range(1,n):
      s=i*ds
      x[i]=x[i-1]+np.cos(s*s)*ds
      y[i]=y[i-1]+np.sin(s*s)*ds
   #scale to the defined rmin@theta2, l=1/r/a**2, theta=l/2/r=1/r^2/a^2/4=a^2*l^2 
   #==> 1/rmin/rmin/a^2/4=thetamax ==>sfactor=a=sqrt(1/thetamax)/2/rmin
    sfactor=np.sqrt(1/theta2)/2/rmin
    x=x/sfactor
    y=y/sfactor    
   
   #add the symmetrical second part
    for i in range(1,n):
      xmid=(np.tan(np.pi/2-theta2)*x[n-1]+y[n-1]+np.tan(theta2)*x[n-i-1]-y[n-i-1])/(np.tan(theta2)+np.tan(np.pi/2-theta2))
      ymid=-np.tan(np.pi/2-theta2)*(xmid-x[n-1])+y[n-1]
      x=np.append(x,x[n-i-1]+2*(xmid-x[n-i-1]))
      y=np.append(y,y[n-i-1]+2*(ymid-y[n-i-1]))
      #x=np.append(x,y[n-1]+x[n-1]-y[n-i-1]) #for 90 degree bend
      #y=np.append(y,y[n-1]+x[n-1]-x[n-i-1]) #for 90 degree bend
    return(x,y)
    
def ebendw(rmin=10, theta=np.pi/2, w=1, n=50):
    #get the center curve
    xyc=ecurvesym(rmin, theta, n)
    xc=xyc[0]
    yc=xyc[1]
    ds=np.sqrt(theta/2)/n
    n2=len(xc)
   #determine the inner and outer outlines
    xouter=np.zeros(n2)
    youter=np.zeros(n2)
    xinner=np.zeros(n2)
    yinner=np.zeros(n2)
    for i in range(0,n):
      thetai=(i*ds)**2
      xouter[i]=xc[i]+w/2*np.sin(thetai)
      youter[i]=yc[i]-w/2*np.cos(thetai)
      xinner[i]=xc[i]-w/2*np.sin(thetai)
      yinner[i]=yc[i]+w/2*np.cos(thetai)
    for i in range(n,n2):
      thetai=theta-((n2-i)*ds)**2
      xouter[i]=xc[i]+w/2*np.sin(thetai)
      youter[i]=yc[i]-w/2*np.cos(thetai)
      xinner[i]=xc[i]-w/2*np.sin(thetai)
      yinner[i]=yc[i]+w/2*np.cos(thetai)
    x=np.append(xinner,xouter[::-1])
    x=np.append(x,xinner[0])
    y=np.append(yinner,youter[::-1])
    y=np.append(y,yinner[0])
    return(x,y)


class Ebend(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the Euler Bend
  """

  def __init__(self):

    # Important: initialize the super class
    super(Ebend, self).__init__()

    # declare the parameters
    self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("s", self.TypeShape, "", default = pya.DPoint(0, 0))
    self.param("rmin", self.TypeDouble, "Min Radius", default = 1)
    self.param("w", self.TypeDouble, "Width", default =1)
    self.param("theta", self.TypeDouble, "Total bending angle", default = 3.14)
    self.param("n", self.TypeInt, "Number of points", default = 50)  

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Euler Bend(W=" + str(self.w) + ",Rmin=" + ('%.3f' % self.rmin) + ")"
    
  def produce_impl(self):
    # This is the main part of the implementation: create the layout
    # fetch the parameters convert database unit
    rmin_dbu = self.rmin / self.layout.dbu
    w_dbu=self.w/self.layout.dbu
   
   #get the outline point coordinates
    pts = []
    xy=ebendw(rmin_dbu, self.theta, w_dbu, int(self.n/2))
    x=xy[0]
    y=xy[1]
    n=len(x)
    
    for i in range(0,n):
      pts.append(pya.Point.from_dpoint(pya.DPoint(x[i],y[i])))

    # create the shape
    self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))


class MyLib(pya.Library):
  """
  The library where we will put the PCell into 
  """

  def __init__(self):
  
    # Set the description
    self.description = "My First Library"
    
    # Create the PCell declarations
    self.layout().register_pcell("Euler Bend", Ebend())
    # That would be the place to put in more PCells ...
    
    # Register us with the name "MyLib".
    # If a library with that name already existed, it will be replaced then.
    self.register("MyLib")


# Instantiate and register the library
MyLib()
