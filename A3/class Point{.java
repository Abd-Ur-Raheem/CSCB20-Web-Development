class Point{
    //Fields 
    private x;
    private y;


    //methods
    public Point(){
        x = 1;
        y = 2;
    }

    public Point(double a, double b){
        x = a;
        y = b;
    }

    public double distanceFromOrigim(){

    }

    public double getX(){
        return x;
    }
}

class Driver{
    public static void main(string [] args){
        Point p1 = new Point (3,4);
        Point p2 = new Point ();
        System.out.println(p2.getX());
    }
}